"""
OAuth2 Manager for Codex platform.

Implements OAuth2 authentication flows with focus on GitHub as the primary provider.
Supports PKCE for security, token refresh, and secure storage.
"""

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Optional
from urllib.parse import urlencode

import httpx

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


@dataclass
class OAuthToken:
    """OAuth token data structure."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: float = 0.0
    
    def __post_init__(self):
        """Set creation timestamp if not provided."""
        if self.created_at == 0.0:
            self.created_at = time.time()
    
    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """
        Check if token is expired or will expire soon.
        
        Args:
            buffer_seconds: Consider token expired this many seconds before actual expiry
        
        Returns:
            True if token is expired or will expire soon
        """
        if self.expires_in <= 0:
            return False  # No expiry set
        
        elapsed = time.time() - self.created_at
        return elapsed >= (self.expires_in - buffer_seconds)


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    provider_name: str
    client_id: str
    client_secret: Optional[str]  # Not needed for PKCE flows
    authorization_url: str
    token_url: str
    redirect_uri: str
    scope: str
    use_pkce: bool = True  # Always use PKCE for security


class OAuthManager:
    """
    OAuth2 authentication manager with GitHub focus.
    
    Implements OAuth2 authorization code flow with PKCE support
    for enhanced security. Handles token exchange, refresh, and
    validation with comprehensive error handling.
    """
    
    # GitHub OAuth endpoints
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_API_URL = "https://api.github.com"
    
    def xǁOAuthManagerǁ__init____mutmut_orig(self, config: Optional[OAuthConfig] = None):
        """
        Initialize OAuth manager.
        
        Args:
            config: Optional OAuth configuration. If not provided, will use GitHub defaults.
        """
        self.config = config
        self._state_store: Dict[str, Dict] = {}  # In-memory state storage (use Redis in production)
        self._token_store: Dict[str, OAuthToken] = {}  # In-memory token storage (use database in production)
        
    
    def xǁOAuthManagerǁ__init____mutmut_1(self, config: Optional[OAuthConfig] = None):
        """
        Initialize OAuth manager.
        
        Args:
            config: Optional OAuth configuration. If not provided, will use GitHub defaults.
        """
        self.config = None
        self._state_store: Dict[str, Dict] = {}  # In-memory state storage (use Redis in production)
        self._token_store: Dict[str, OAuthToken] = {}  # In-memory token storage (use database in production)
        
    
    def xǁOAuthManagerǁ__init____mutmut_2(self, config: Optional[OAuthConfig] = None):
        """
        Initialize OAuth manager.
        
        Args:
            config: Optional OAuth configuration. If not provided, will use GitHub defaults.
        """
        self.config = config
        self._state_store: Dict[str, Dict] = None  # In-memory state storage (use Redis in production)
        self._token_store: Dict[str, OAuthToken] = {}  # In-memory token storage (use database in production)
        
    
    def xǁOAuthManagerǁ__init____mutmut_3(self, config: Optional[OAuthConfig] = None):
        """
        Initialize OAuth manager.
        
        Args:
            config: Optional OAuth configuration. If not provided, will use GitHub defaults.
        """
        self.config = config
        self._state_store: Dict[str, Dict] = {}  # In-memory state storage (use Redis in production)
        self._token_store: Dict[str, OAuthToken] = None  # In-memory token storage (use database in production)
        
    
    xǁOAuthManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁ__init____mutmut_1': xǁOAuthManagerǁ__init____mutmut_1, 
        'xǁOAuthManagerǁ__init____mutmut_2': xǁOAuthManagerǁ__init____mutmut_2, 
        'xǁOAuthManagerǁ__init____mutmut_3': xǁOAuthManagerǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁOAuthManagerǁ__init____mutmut_orig)
    xǁOAuthManagerǁ__init____mutmut_orig.__name__ = 'xǁOAuthManagerǁ__init__'
    def xǁOAuthManagerǁcreate_github_config__mutmut_orig(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_1(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "XXrepo userXX") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_2(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "REPO USER") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_3(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name=None,
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_4(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=None,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_5(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=None,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_6(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=None,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_7(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=None,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_8(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=None,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_9(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=None,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_10(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=None,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_11(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_12(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_13(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_14(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_15(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_16(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_17(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_18(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            )
    def xǁOAuthManagerǁcreate_github_config__mutmut_19(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="XXgithubXX",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_20(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="GITHUB",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=True,  # Always use PKCE for security
        )
    def xǁOAuthManagerǁcreate_github_config__mutmut_21(self, client_id: str, client_secret: Optional[str], 
                           redirect_uri: str, scope: str = "repo user") -> OAuthConfig:
        """
        Create GitHub OAuth configuration.
        
        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret (optional for PKCE)
            redirect_uri: Redirect URI registered with GitHub
            scope: OAuth scopes (default: repo, user)
        
        Returns:
            OAuthConfig for GitHub
        """
        return OAuthConfig(
            provider_name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=self.GITHUB_AUTH_URL,
            token_url=self.GITHUB_TOKEN_URL,
            redirect_uri=redirect_uri,
            scope=scope,
            use_pkce=False,  # Always use PKCE for security
        )
    
    xǁOAuthManagerǁcreate_github_config__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁcreate_github_config__mutmut_1': xǁOAuthManagerǁcreate_github_config__mutmut_1, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_2': xǁOAuthManagerǁcreate_github_config__mutmut_2, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_3': xǁOAuthManagerǁcreate_github_config__mutmut_3, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_4': xǁOAuthManagerǁcreate_github_config__mutmut_4, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_5': xǁOAuthManagerǁcreate_github_config__mutmut_5, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_6': xǁOAuthManagerǁcreate_github_config__mutmut_6, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_7': xǁOAuthManagerǁcreate_github_config__mutmut_7, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_8': xǁOAuthManagerǁcreate_github_config__mutmut_8, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_9': xǁOAuthManagerǁcreate_github_config__mutmut_9, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_10': xǁOAuthManagerǁcreate_github_config__mutmut_10, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_11': xǁOAuthManagerǁcreate_github_config__mutmut_11, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_12': xǁOAuthManagerǁcreate_github_config__mutmut_12, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_13': xǁOAuthManagerǁcreate_github_config__mutmut_13, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_14': xǁOAuthManagerǁcreate_github_config__mutmut_14, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_15': xǁOAuthManagerǁcreate_github_config__mutmut_15, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_16': xǁOAuthManagerǁcreate_github_config__mutmut_16, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_17': xǁOAuthManagerǁcreate_github_config__mutmut_17, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_18': xǁOAuthManagerǁcreate_github_config__mutmut_18, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_19': xǁOAuthManagerǁcreate_github_config__mutmut_19, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_20': xǁOAuthManagerǁcreate_github_config__mutmut_20, 
        'xǁOAuthManagerǁcreate_github_config__mutmut_21': xǁOAuthManagerǁcreate_github_config__mutmut_21
    }
    
    def create_github_config(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁcreate_github_config__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁcreate_github_config__mutmut_mutants"), args, kwargs, self)
        return result 
    
    create_github_config.__signature__ = _mutmut_signature(xǁOAuthManagerǁcreate_github_config__mutmut_orig)
    xǁOAuthManagerǁcreate_github_config__mutmut_orig.__name__ = 'xǁOAuthManagerǁcreate_github_config'
    
    def xǁOAuthManagerǁ_generate_state__mutmut_orig(self) -> str:
        """Generate secure random state for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    def xǁOAuthManagerǁ_generate_state__mutmut_1(self) -> str:
        """Generate secure random state for CSRF protection."""
        return secrets.token_urlsafe(None)
    
    def xǁOAuthManagerǁ_generate_state__mutmut_2(self) -> str:
        """Generate secure random state for CSRF protection."""
        return secrets.token_urlsafe(33)
    
    xǁOAuthManagerǁ_generate_state__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁ_generate_state__mutmut_1': xǁOAuthManagerǁ_generate_state__mutmut_1, 
        'xǁOAuthManagerǁ_generate_state__mutmut_2': xǁOAuthManagerǁ_generate_state__mutmut_2
    }
    
    def _generate_state(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁ_generate_state__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁ_generate_state__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_state.__signature__ = _mutmut_signature(xǁOAuthManagerǁ_generate_state__mutmut_orig)
    xǁOAuthManagerǁ_generate_state__mutmut_orig.__name__ = 'xǁOAuthManagerǁ_generate_state'
    
    def xǁOAuthManagerǁ_generate_code_verifier__mutmut_orig(self) -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(64)
    
    def xǁOAuthManagerǁ_generate_code_verifier__mutmut_1(self) -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(None)
    
    def xǁOAuthManagerǁ_generate_code_verifier__mutmut_2(self) -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(65)
    
    xǁOAuthManagerǁ_generate_code_verifier__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁ_generate_code_verifier__mutmut_1': xǁOAuthManagerǁ_generate_code_verifier__mutmut_1, 
        'xǁOAuthManagerǁ_generate_code_verifier__mutmut_2': xǁOAuthManagerǁ_generate_code_verifier__mutmut_2
    }
    
    def _generate_code_verifier(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁ_generate_code_verifier__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁ_generate_code_verifier__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_code_verifier.__signature__ = _mutmut_signature(xǁOAuthManagerǁ_generate_code_verifier__mutmut_orig)
    xǁOAuthManagerǁ_generate_code_verifier__mutmut_orig.__name__ = 'xǁOAuthManagerǁ_generate_code_verifier'
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_orig(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_1(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = None
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_2(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(None).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_3(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = None
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_4(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip(None)
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_5(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().lstrip('=')
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_6(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(None).decode().rstrip('=')
        return challenge
    
    def xǁOAuthManagerǁ_generate_code_challenge__mutmut_7(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip('XX=XX')
        return challenge
    
    xǁOAuthManagerǁ_generate_code_challenge__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁ_generate_code_challenge__mutmut_1': xǁOAuthManagerǁ_generate_code_challenge__mutmut_1, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_2': xǁOAuthManagerǁ_generate_code_challenge__mutmut_2, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_3': xǁOAuthManagerǁ_generate_code_challenge__mutmut_3, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_4': xǁOAuthManagerǁ_generate_code_challenge__mutmut_4, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_5': xǁOAuthManagerǁ_generate_code_challenge__mutmut_5, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_6': xǁOAuthManagerǁ_generate_code_challenge__mutmut_6, 
        'xǁOAuthManagerǁ_generate_code_challenge__mutmut_7': xǁOAuthManagerǁ_generate_code_challenge__mutmut_7
    }
    
    def _generate_code_challenge(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁ_generate_code_challenge__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁ_generate_code_challenge__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_code_challenge.__signature__ = _mutmut_signature(xǁOAuthManagerǁ_generate_code_challenge__mutmut_orig)
    xǁOAuthManagerǁ_generate_code_challenge__mutmut_orig.__name__ = 'xǁOAuthManagerǁ_generate_code_challenge'
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_orig(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_1(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is not None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_2(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = None
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_3(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is not None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_4(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError(None)
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_5(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("XXOAuth configuration is requiredXX")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_6(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("oauth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_7(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAUTH CONFIGURATION IS REQUIRED")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_8(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = None
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_9(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = None
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_10(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'XXclient_idXX': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_11(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'CLIENT_ID': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_12(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'XXredirect_uriXX': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_13(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'REDIRECT_URI': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_14(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'XXscopeXX': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_15(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'SCOPE': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_16(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'XXstateXX': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_17(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'STATE': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_18(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'XXresponse_typeXX': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_19(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'RESPONSE_TYPE': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_20(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'XXcodeXX',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_21(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'CODE',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_22(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = ""
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_23(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = None
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_24(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = None
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_25(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(None)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_26(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = None
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_27(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['XXcode_challengeXX'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_28(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['CODE_CHALLENGE'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_29(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = None
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_30(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['XXcode_challenge_methodXX'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_31(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['CODE_CHALLENGE_METHOD'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_32(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'XXS256XX'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_33(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 's256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_34(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = None
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_35(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'XXcreated_atXX': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_36(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'CREATED_AT': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_37(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'XXconfigXX': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_38(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'CONFIG': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_39(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'XXcode_verifierXX': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_40(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'CODE_VERIFIER': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_41(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = None
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_42(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(None)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_43(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'XXauth_urlXX': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_44(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'AUTH_URL': auth_url,
            'state': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_45(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'XXstateXX': state,
        }
    
    def xǁOAuthManagerǁinitiate_flow__mutmut_46(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
        """
        Initiate OAuth2 authorization flow.
        
        Args:
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            Dictionary with 'auth_url' and 'state' keys
        
        Raises:
            ValueError: If no configuration is available
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Generate state for CSRF protection
        state = self._generate_state()
        
        # Prepare authorization parameters
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'scope': config.scope,
            'state': state,
            'response_type': 'code',
        }
        
        # Add PKCE parameters if enabled
        code_verifier = None
        if config.use_pkce:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        # Store state and code_verifier for validation
        self._state_store[state] = {
            'created_at': time.time(),
            'config': config,
            'code_verifier': code_verifier,
        }
        
        # Build authorization URL
        auth_url = f"{config.authorization_url}?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'STATE': state,
        }
    
    xǁOAuthManagerǁinitiate_flow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁinitiate_flow__mutmut_1': xǁOAuthManagerǁinitiate_flow__mutmut_1, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_2': xǁOAuthManagerǁinitiate_flow__mutmut_2, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_3': xǁOAuthManagerǁinitiate_flow__mutmut_3, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_4': xǁOAuthManagerǁinitiate_flow__mutmut_4, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_5': xǁOAuthManagerǁinitiate_flow__mutmut_5, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_6': xǁOAuthManagerǁinitiate_flow__mutmut_6, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_7': xǁOAuthManagerǁinitiate_flow__mutmut_7, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_8': xǁOAuthManagerǁinitiate_flow__mutmut_8, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_9': xǁOAuthManagerǁinitiate_flow__mutmut_9, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_10': xǁOAuthManagerǁinitiate_flow__mutmut_10, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_11': xǁOAuthManagerǁinitiate_flow__mutmut_11, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_12': xǁOAuthManagerǁinitiate_flow__mutmut_12, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_13': xǁOAuthManagerǁinitiate_flow__mutmut_13, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_14': xǁOAuthManagerǁinitiate_flow__mutmut_14, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_15': xǁOAuthManagerǁinitiate_flow__mutmut_15, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_16': xǁOAuthManagerǁinitiate_flow__mutmut_16, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_17': xǁOAuthManagerǁinitiate_flow__mutmut_17, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_18': xǁOAuthManagerǁinitiate_flow__mutmut_18, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_19': xǁOAuthManagerǁinitiate_flow__mutmut_19, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_20': xǁOAuthManagerǁinitiate_flow__mutmut_20, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_21': xǁOAuthManagerǁinitiate_flow__mutmut_21, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_22': xǁOAuthManagerǁinitiate_flow__mutmut_22, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_23': xǁOAuthManagerǁinitiate_flow__mutmut_23, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_24': xǁOAuthManagerǁinitiate_flow__mutmut_24, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_25': xǁOAuthManagerǁinitiate_flow__mutmut_25, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_26': xǁOAuthManagerǁinitiate_flow__mutmut_26, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_27': xǁOAuthManagerǁinitiate_flow__mutmut_27, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_28': xǁOAuthManagerǁinitiate_flow__mutmut_28, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_29': xǁOAuthManagerǁinitiate_flow__mutmut_29, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_30': xǁOAuthManagerǁinitiate_flow__mutmut_30, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_31': xǁOAuthManagerǁinitiate_flow__mutmut_31, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_32': xǁOAuthManagerǁinitiate_flow__mutmut_32, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_33': xǁOAuthManagerǁinitiate_flow__mutmut_33, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_34': xǁOAuthManagerǁinitiate_flow__mutmut_34, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_35': xǁOAuthManagerǁinitiate_flow__mutmut_35, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_36': xǁOAuthManagerǁinitiate_flow__mutmut_36, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_37': xǁOAuthManagerǁinitiate_flow__mutmut_37, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_38': xǁOAuthManagerǁinitiate_flow__mutmut_38, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_39': xǁOAuthManagerǁinitiate_flow__mutmut_39, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_40': xǁOAuthManagerǁinitiate_flow__mutmut_40, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_41': xǁOAuthManagerǁinitiate_flow__mutmut_41, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_42': xǁOAuthManagerǁinitiate_flow__mutmut_42, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_43': xǁOAuthManagerǁinitiate_flow__mutmut_43, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_44': xǁOAuthManagerǁinitiate_flow__mutmut_44, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_45': xǁOAuthManagerǁinitiate_flow__mutmut_45, 
        'xǁOAuthManagerǁinitiate_flow__mutmut_46': xǁOAuthManagerǁinitiate_flow__mutmut_46
    }
    
    def initiate_flow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁinitiate_flow__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁinitiate_flow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    initiate_flow.__signature__ = _mutmut_signature(xǁOAuthManagerǁinitiate_flow__mutmut_orig)
    xǁOAuthManagerǁinitiate_flow__mutmut_orig.__name__ = 'xǁOAuthManagerǁinitiate_flow'
    
    def xǁOAuthManagerǁvalidate_state__mutmut_orig(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_1(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_2(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return True
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_3(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = None
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_4(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = None
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_5(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() + state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_6(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['XXcreated_atXX']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_7(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['CREATED_AT']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_8(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age >= 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_9(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 901:  # 15 minutes
            del self._state_store[state]
            return False
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_10(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return True
        
        return True
    
    def xǁOAuthManagerǁvalidate_state__mutmut_11(self, state: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State parameter from callback
        
        Returns:
            True if state is valid, False otherwise
        """
        if state not in self._state_store:
            return False
        
        # Check state expiry (15 minutes)
        state_data = self._state_store[state]
        age = time.time() - state_data['created_at']
        if age > 900:  # 15 minutes
            del self._state_store[state]
            return False
        
        return False
    
    xǁOAuthManagerǁvalidate_state__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁvalidate_state__mutmut_1': xǁOAuthManagerǁvalidate_state__mutmut_1, 
        'xǁOAuthManagerǁvalidate_state__mutmut_2': xǁOAuthManagerǁvalidate_state__mutmut_2, 
        'xǁOAuthManagerǁvalidate_state__mutmut_3': xǁOAuthManagerǁvalidate_state__mutmut_3, 
        'xǁOAuthManagerǁvalidate_state__mutmut_4': xǁOAuthManagerǁvalidate_state__mutmut_4, 
        'xǁOAuthManagerǁvalidate_state__mutmut_5': xǁOAuthManagerǁvalidate_state__mutmut_5, 
        'xǁOAuthManagerǁvalidate_state__mutmut_6': xǁOAuthManagerǁvalidate_state__mutmut_6, 
        'xǁOAuthManagerǁvalidate_state__mutmut_7': xǁOAuthManagerǁvalidate_state__mutmut_7, 
        'xǁOAuthManagerǁvalidate_state__mutmut_8': xǁOAuthManagerǁvalidate_state__mutmut_8, 
        'xǁOAuthManagerǁvalidate_state__mutmut_9': xǁOAuthManagerǁvalidate_state__mutmut_9, 
        'xǁOAuthManagerǁvalidate_state__mutmut_10': xǁOAuthManagerǁvalidate_state__mutmut_10, 
        'xǁOAuthManagerǁvalidate_state__mutmut_11': xǁOAuthManagerǁvalidate_state__mutmut_11
    }
    
    def validate_state(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁvalidate_state__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁvalidate_state__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_state.__signature__ = _mutmut_signature(xǁOAuthManagerǁvalidate_state__mutmut_orig)
    xǁOAuthManagerǁvalidate_state__mutmut_orig.__name__ = 'xǁOAuthManagerǁvalidate_state'
    
    def xǁOAuthManagerǁexchange_code__mutmut_orig(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_1(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_2(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(None):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_3(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError(None)
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_4(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("XXInvalid or expired state parameterXX")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_5(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_6(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("INVALID OR EXPIRED STATE PARAMETER")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_7(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = None
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_8(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(None)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_9(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = None
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_10(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['XXconfigXX']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_11(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['CONFIG']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_12(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = None
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_13(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get(None)
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_14(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('XXcode_verifierXX')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_15(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('CODE_VERIFIER')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_16(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = None
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_17(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'XXclient_idXX': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_18(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'CLIENT_ID': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_19(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'XXcodeXX': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_20(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'CODE': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_21(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'XXredirect_uriXX': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_22(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'REDIRECT_URI': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_23(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = None
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_24(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['XXclient_secretXX'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_25(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['CLIENT_SECRET'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_26(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = None
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_27(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['XXcode_verifierXX'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_28(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['CODE_VERIFIER'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_29(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = None
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_30(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'XXAcceptXX': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_31(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_32(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'ACCEPT': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_33(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'XXapplication/jsonXX',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_34(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'APPLICATION/JSON',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_35(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'XXContent-TypeXX': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_36(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_37(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'CONTENT-TYPE': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_38(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'XXapplication/x-www-form-urlencodedXX',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_39(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'APPLICATION/X-WWW-FORM-URLENCODED',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_40(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = None
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_41(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    None,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_42(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=None,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_43(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=None,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_44(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=None,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_45(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_46(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_47(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_48(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_49(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=31.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_50(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = None
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_51(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = None
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_52(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(None)
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_53(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(None)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_54(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(None)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_55(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = None
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_56(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get(None)
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_57(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('XXaccess_tokenXX')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_58(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('ACCESS_TOKEN')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_59(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_60(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError(None)
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_61(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("XXNo access token in responseXX")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_62(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("no access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_63(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("NO ACCESS TOKEN IN RESPONSE")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_64(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = None
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_65(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=None,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_66(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=None,
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_67(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=None,
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_68(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=None,
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_69(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=None,
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_70(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_71(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_72(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_73(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_74(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_75(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get(None, 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_76(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', None),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_77(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_78(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', ),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_79(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('XXtoken_typeXX', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_80(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('TOKEN_TYPE', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_81(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'XXbearerXX'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_82(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'BEARER'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_83(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get(None, 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_84(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', None),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_85(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get(0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_86(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', ),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_87(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('XXexpires_inXX', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_88(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('EXPIRES_IN', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_89(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 1),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_90(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get(None),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_91(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('XXrefresh_tokenXX'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_92(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('REFRESH_TOKEN'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_93(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get(None),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_94(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('XXscopeXX'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_95(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('SCOPE'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_96(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = None
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_97(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(None)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_98(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(17)
        self._token_store[token_id] = token
        
        return token
    
    def xǁOAuthManagerǁexchange_code__mutmut_99(self, code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter from callback
        
        Returns:
            OAuthToken with access token and metadata
        
        Raises:
            ValueError: If state is invalid or code exchange fails
        """
        # Validate state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state parameter")
        
        # Retrieve stored state data
        state_data = self._state_store.pop(state)
        config = state_data['config']
        code_verifier = state_data.get('code_verifier')
        
        # Prepare token request
        token_data = {
            'client_id': config.client_id,
            'code': code,
            'redirect_uri': config.redirect_uri,
        }
        
        # Add client_secret if available (not using PKCE-only flow)
        if config.client_secret:
            token_data['client_secret'] = config.client_secret
        
        # Add code_verifier for PKCE
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        
        # Make token request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            # Sanitize error message before logging
            error_msg = sanitize_log_message(f"Token exchange failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse token response
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope'),
        )
        
        # Store token (use user ID as key in production)
        token_id = secrets.token_urlsafe(16)
        self._token_store[token_id] = None
        
        return token
    
    xǁOAuthManagerǁexchange_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁexchange_code__mutmut_1': xǁOAuthManagerǁexchange_code__mutmut_1, 
        'xǁOAuthManagerǁexchange_code__mutmut_2': xǁOAuthManagerǁexchange_code__mutmut_2, 
        'xǁOAuthManagerǁexchange_code__mutmut_3': xǁOAuthManagerǁexchange_code__mutmut_3, 
        'xǁOAuthManagerǁexchange_code__mutmut_4': xǁOAuthManagerǁexchange_code__mutmut_4, 
        'xǁOAuthManagerǁexchange_code__mutmut_5': xǁOAuthManagerǁexchange_code__mutmut_5, 
        'xǁOAuthManagerǁexchange_code__mutmut_6': xǁOAuthManagerǁexchange_code__mutmut_6, 
        'xǁOAuthManagerǁexchange_code__mutmut_7': xǁOAuthManagerǁexchange_code__mutmut_7, 
        'xǁOAuthManagerǁexchange_code__mutmut_8': xǁOAuthManagerǁexchange_code__mutmut_8, 
        'xǁOAuthManagerǁexchange_code__mutmut_9': xǁOAuthManagerǁexchange_code__mutmut_9, 
        'xǁOAuthManagerǁexchange_code__mutmut_10': xǁOAuthManagerǁexchange_code__mutmut_10, 
        'xǁOAuthManagerǁexchange_code__mutmut_11': xǁOAuthManagerǁexchange_code__mutmut_11, 
        'xǁOAuthManagerǁexchange_code__mutmut_12': xǁOAuthManagerǁexchange_code__mutmut_12, 
        'xǁOAuthManagerǁexchange_code__mutmut_13': xǁOAuthManagerǁexchange_code__mutmut_13, 
        'xǁOAuthManagerǁexchange_code__mutmut_14': xǁOAuthManagerǁexchange_code__mutmut_14, 
        'xǁOAuthManagerǁexchange_code__mutmut_15': xǁOAuthManagerǁexchange_code__mutmut_15, 
        'xǁOAuthManagerǁexchange_code__mutmut_16': xǁOAuthManagerǁexchange_code__mutmut_16, 
        'xǁOAuthManagerǁexchange_code__mutmut_17': xǁOAuthManagerǁexchange_code__mutmut_17, 
        'xǁOAuthManagerǁexchange_code__mutmut_18': xǁOAuthManagerǁexchange_code__mutmut_18, 
        'xǁOAuthManagerǁexchange_code__mutmut_19': xǁOAuthManagerǁexchange_code__mutmut_19, 
        'xǁOAuthManagerǁexchange_code__mutmut_20': xǁOAuthManagerǁexchange_code__mutmut_20, 
        'xǁOAuthManagerǁexchange_code__mutmut_21': xǁOAuthManagerǁexchange_code__mutmut_21, 
        'xǁOAuthManagerǁexchange_code__mutmut_22': xǁOAuthManagerǁexchange_code__mutmut_22, 
        'xǁOAuthManagerǁexchange_code__mutmut_23': xǁOAuthManagerǁexchange_code__mutmut_23, 
        'xǁOAuthManagerǁexchange_code__mutmut_24': xǁOAuthManagerǁexchange_code__mutmut_24, 
        'xǁOAuthManagerǁexchange_code__mutmut_25': xǁOAuthManagerǁexchange_code__mutmut_25, 
        'xǁOAuthManagerǁexchange_code__mutmut_26': xǁOAuthManagerǁexchange_code__mutmut_26, 
        'xǁOAuthManagerǁexchange_code__mutmut_27': xǁOAuthManagerǁexchange_code__mutmut_27, 
        'xǁOAuthManagerǁexchange_code__mutmut_28': xǁOAuthManagerǁexchange_code__mutmut_28, 
        'xǁOAuthManagerǁexchange_code__mutmut_29': xǁOAuthManagerǁexchange_code__mutmut_29, 
        'xǁOAuthManagerǁexchange_code__mutmut_30': xǁOAuthManagerǁexchange_code__mutmut_30, 
        'xǁOAuthManagerǁexchange_code__mutmut_31': xǁOAuthManagerǁexchange_code__mutmut_31, 
        'xǁOAuthManagerǁexchange_code__mutmut_32': xǁOAuthManagerǁexchange_code__mutmut_32, 
        'xǁOAuthManagerǁexchange_code__mutmut_33': xǁOAuthManagerǁexchange_code__mutmut_33, 
        'xǁOAuthManagerǁexchange_code__mutmut_34': xǁOAuthManagerǁexchange_code__mutmut_34, 
        'xǁOAuthManagerǁexchange_code__mutmut_35': xǁOAuthManagerǁexchange_code__mutmut_35, 
        'xǁOAuthManagerǁexchange_code__mutmut_36': xǁOAuthManagerǁexchange_code__mutmut_36, 
        'xǁOAuthManagerǁexchange_code__mutmut_37': xǁOAuthManagerǁexchange_code__mutmut_37, 
        'xǁOAuthManagerǁexchange_code__mutmut_38': xǁOAuthManagerǁexchange_code__mutmut_38, 
        'xǁOAuthManagerǁexchange_code__mutmut_39': xǁOAuthManagerǁexchange_code__mutmut_39, 
        'xǁOAuthManagerǁexchange_code__mutmut_40': xǁOAuthManagerǁexchange_code__mutmut_40, 
        'xǁOAuthManagerǁexchange_code__mutmut_41': xǁOAuthManagerǁexchange_code__mutmut_41, 
        'xǁOAuthManagerǁexchange_code__mutmut_42': xǁOAuthManagerǁexchange_code__mutmut_42, 
        'xǁOAuthManagerǁexchange_code__mutmut_43': xǁOAuthManagerǁexchange_code__mutmut_43, 
        'xǁOAuthManagerǁexchange_code__mutmut_44': xǁOAuthManagerǁexchange_code__mutmut_44, 
        'xǁOAuthManagerǁexchange_code__mutmut_45': xǁOAuthManagerǁexchange_code__mutmut_45, 
        'xǁOAuthManagerǁexchange_code__mutmut_46': xǁOAuthManagerǁexchange_code__mutmut_46, 
        'xǁOAuthManagerǁexchange_code__mutmut_47': xǁOAuthManagerǁexchange_code__mutmut_47, 
        'xǁOAuthManagerǁexchange_code__mutmut_48': xǁOAuthManagerǁexchange_code__mutmut_48, 
        'xǁOAuthManagerǁexchange_code__mutmut_49': xǁOAuthManagerǁexchange_code__mutmut_49, 
        'xǁOAuthManagerǁexchange_code__mutmut_50': xǁOAuthManagerǁexchange_code__mutmut_50, 
        'xǁOAuthManagerǁexchange_code__mutmut_51': xǁOAuthManagerǁexchange_code__mutmut_51, 
        'xǁOAuthManagerǁexchange_code__mutmut_52': xǁOAuthManagerǁexchange_code__mutmut_52, 
        'xǁOAuthManagerǁexchange_code__mutmut_53': xǁOAuthManagerǁexchange_code__mutmut_53, 
        'xǁOAuthManagerǁexchange_code__mutmut_54': xǁOAuthManagerǁexchange_code__mutmut_54, 
        'xǁOAuthManagerǁexchange_code__mutmut_55': xǁOAuthManagerǁexchange_code__mutmut_55, 
        'xǁOAuthManagerǁexchange_code__mutmut_56': xǁOAuthManagerǁexchange_code__mutmut_56, 
        'xǁOAuthManagerǁexchange_code__mutmut_57': xǁOAuthManagerǁexchange_code__mutmut_57, 
        'xǁOAuthManagerǁexchange_code__mutmut_58': xǁOAuthManagerǁexchange_code__mutmut_58, 
        'xǁOAuthManagerǁexchange_code__mutmut_59': xǁOAuthManagerǁexchange_code__mutmut_59, 
        'xǁOAuthManagerǁexchange_code__mutmut_60': xǁOAuthManagerǁexchange_code__mutmut_60, 
        'xǁOAuthManagerǁexchange_code__mutmut_61': xǁOAuthManagerǁexchange_code__mutmut_61, 
        'xǁOAuthManagerǁexchange_code__mutmut_62': xǁOAuthManagerǁexchange_code__mutmut_62, 
        'xǁOAuthManagerǁexchange_code__mutmut_63': xǁOAuthManagerǁexchange_code__mutmut_63, 
        'xǁOAuthManagerǁexchange_code__mutmut_64': xǁOAuthManagerǁexchange_code__mutmut_64, 
        'xǁOAuthManagerǁexchange_code__mutmut_65': xǁOAuthManagerǁexchange_code__mutmut_65, 
        'xǁOAuthManagerǁexchange_code__mutmut_66': xǁOAuthManagerǁexchange_code__mutmut_66, 
        'xǁOAuthManagerǁexchange_code__mutmut_67': xǁOAuthManagerǁexchange_code__mutmut_67, 
        'xǁOAuthManagerǁexchange_code__mutmut_68': xǁOAuthManagerǁexchange_code__mutmut_68, 
        'xǁOAuthManagerǁexchange_code__mutmut_69': xǁOAuthManagerǁexchange_code__mutmut_69, 
        'xǁOAuthManagerǁexchange_code__mutmut_70': xǁOAuthManagerǁexchange_code__mutmut_70, 
        'xǁOAuthManagerǁexchange_code__mutmut_71': xǁOAuthManagerǁexchange_code__mutmut_71, 
        'xǁOAuthManagerǁexchange_code__mutmut_72': xǁOAuthManagerǁexchange_code__mutmut_72, 
        'xǁOAuthManagerǁexchange_code__mutmut_73': xǁOAuthManagerǁexchange_code__mutmut_73, 
        'xǁOAuthManagerǁexchange_code__mutmut_74': xǁOAuthManagerǁexchange_code__mutmut_74, 
        'xǁOAuthManagerǁexchange_code__mutmut_75': xǁOAuthManagerǁexchange_code__mutmut_75, 
        'xǁOAuthManagerǁexchange_code__mutmut_76': xǁOAuthManagerǁexchange_code__mutmut_76, 
        'xǁOAuthManagerǁexchange_code__mutmut_77': xǁOAuthManagerǁexchange_code__mutmut_77, 
        'xǁOAuthManagerǁexchange_code__mutmut_78': xǁOAuthManagerǁexchange_code__mutmut_78, 
        'xǁOAuthManagerǁexchange_code__mutmut_79': xǁOAuthManagerǁexchange_code__mutmut_79, 
        'xǁOAuthManagerǁexchange_code__mutmut_80': xǁOAuthManagerǁexchange_code__mutmut_80, 
        'xǁOAuthManagerǁexchange_code__mutmut_81': xǁOAuthManagerǁexchange_code__mutmut_81, 
        'xǁOAuthManagerǁexchange_code__mutmut_82': xǁOAuthManagerǁexchange_code__mutmut_82, 
        'xǁOAuthManagerǁexchange_code__mutmut_83': xǁOAuthManagerǁexchange_code__mutmut_83, 
        'xǁOAuthManagerǁexchange_code__mutmut_84': xǁOAuthManagerǁexchange_code__mutmut_84, 
        'xǁOAuthManagerǁexchange_code__mutmut_85': xǁOAuthManagerǁexchange_code__mutmut_85, 
        'xǁOAuthManagerǁexchange_code__mutmut_86': xǁOAuthManagerǁexchange_code__mutmut_86, 
        'xǁOAuthManagerǁexchange_code__mutmut_87': xǁOAuthManagerǁexchange_code__mutmut_87, 
        'xǁOAuthManagerǁexchange_code__mutmut_88': xǁOAuthManagerǁexchange_code__mutmut_88, 
        'xǁOAuthManagerǁexchange_code__mutmut_89': xǁOAuthManagerǁexchange_code__mutmut_89, 
        'xǁOAuthManagerǁexchange_code__mutmut_90': xǁOAuthManagerǁexchange_code__mutmut_90, 
        'xǁOAuthManagerǁexchange_code__mutmut_91': xǁOAuthManagerǁexchange_code__mutmut_91, 
        'xǁOAuthManagerǁexchange_code__mutmut_92': xǁOAuthManagerǁexchange_code__mutmut_92, 
        'xǁOAuthManagerǁexchange_code__mutmut_93': xǁOAuthManagerǁexchange_code__mutmut_93, 
        'xǁOAuthManagerǁexchange_code__mutmut_94': xǁOAuthManagerǁexchange_code__mutmut_94, 
        'xǁOAuthManagerǁexchange_code__mutmut_95': xǁOAuthManagerǁexchange_code__mutmut_95, 
        'xǁOAuthManagerǁexchange_code__mutmut_96': xǁOAuthManagerǁexchange_code__mutmut_96, 
        'xǁOAuthManagerǁexchange_code__mutmut_97': xǁOAuthManagerǁexchange_code__mutmut_97, 
        'xǁOAuthManagerǁexchange_code__mutmut_98': xǁOAuthManagerǁexchange_code__mutmut_98, 
        'xǁOAuthManagerǁexchange_code__mutmut_99': xǁOAuthManagerǁexchange_code__mutmut_99
    }
    
    def exchange_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁexchange_code__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁexchange_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    exchange_code.__signature__ = _mutmut_signature(xǁOAuthManagerǁexchange_code__mutmut_orig)
    xǁOAuthManagerǁexchange_code__mutmut_orig.__name__ = 'xǁOAuthManagerǁexchange_code'
    
    def xǁOAuthManagerǁrefresh_token__mutmut_orig(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_1(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is not None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_2(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = None
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_3(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is not None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_4(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError(None)
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_5(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("XXOAuth configuration is requiredXX")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_6(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("oauth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_7(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAUTH CONFIGURATION IS REQUIRED")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_8(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = None
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_9(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'XXclient_idXX': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_10(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'CLIENT_ID': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_11(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'XXclient_secretXX': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_12(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'CLIENT_SECRET': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_13(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'XXrefresh_tokenXX': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_14(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'REFRESH_TOKEN': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_15(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'XXgrant_typeXX': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_16(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'GRANT_TYPE': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_17(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'XXrefresh_tokenXX',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_18(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'REFRESH_TOKEN',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_19(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = None
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_20(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'XXAcceptXX': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_21(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_22(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'ACCEPT': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_23(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'XXapplication/jsonXX',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_24(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'APPLICATION/JSON',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_25(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'XXContent-TypeXX': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_26(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_27(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'CONTENT-TYPE': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_28(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'XXapplication/x-www-form-urlencodedXX',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_29(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'APPLICATION/X-WWW-FORM-URLENCODED',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_30(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = None
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_31(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    None,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_32(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=None,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_33(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=None,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_34(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=None,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_35(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_36(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_37(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_38(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_39(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=31.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_40(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = None
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_41(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = None
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_42(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(None)
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_43(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(None)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_44(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(None)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_45(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = None
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_46(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get(None)
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_47(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('XXaccess_tokenXX')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_48(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('ACCESS_TOKEN')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_49(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_50(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError(None)
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_51(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("XXNo access token in refresh responseXX")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_52(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("no access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_53(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("NO ACCESS TOKEN IN REFRESH RESPONSE")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_54(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = None
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_55(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=None,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_56(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=None,
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_57(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=None,
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_58(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=None,  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_59(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=None,
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_60(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_61(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_62(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_63(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_64(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_65(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get(None, 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_66(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', None),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_67(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_68(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', ),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_69(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('XXtoken_typeXX', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_70(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('TOKEN_TYPE', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_71(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'XXbearerXX'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_72(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'BEARER'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_73(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get(None, 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_74(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', None),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_75(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get(0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_76(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', ),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_77(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('XXexpires_inXX', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_78(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('EXPIRES_IN', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_79(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 1),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_80(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get(None, refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_81(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', None),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_82(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get(refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_83(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', ),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_84(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('XXrefresh_tokenXX', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_85(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('REFRESH_TOKEN', refresh_token),  # Use old if not provided
            scope=token_response.get('scope'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_86(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get(None),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_87(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('XXscopeXX'),
        )
        
        return token
    
    def xǁOAuthManagerǁrefresh_token__mutmut_88(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            config: OAuth configuration (uses self.config if not provided)
        
        Returns:
            New OAuthToken with refreshed access token
        
        Raises:
            ValueError: If refresh fails
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("OAuth configuration is required")
        
        # Prepare refresh request
        refresh_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    config.token_url,
                    data=refresh_data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"Token refresh failed: {str(e)}")
            raise ValueError(error_msg)
        
        # Parse refreshed token
        access_token = token_response.get('access_token')
        if not access_token:
            raise ValueError("No access token in refresh response")
        
        token = OAuthToken(
            access_token=access_token,
            token_type=token_response.get('token_type', 'bearer'),
            expires_in=token_response.get('expires_in', 0),
            refresh_token=token_response.get('refresh_token', refresh_token),  # Use old if not provided
            scope=token_response.get('SCOPE'),
        )
        
        return token
    
    xǁOAuthManagerǁrefresh_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁrefresh_token__mutmut_1': xǁOAuthManagerǁrefresh_token__mutmut_1, 
        'xǁOAuthManagerǁrefresh_token__mutmut_2': xǁOAuthManagerǁrefresh_token__mutmut_2, 
        'xǁOAuthManagerǁrefresh_token__mutmut_3': xǁOAuthManagerǁrefresh_token__mutmut_3, 
        'xǁOAuthManagerǁrefresh_token__mutmut_4': xǁOAuthManagerǁrefresh_token__mutmut_4, 
        'xǁOAuthManagerǁrefresh_token__mutmut_5': xǁOAuthManagerǁrefresh_token__mutmut_5, 
        'xǁOAuthManagerǁrefresh_token__mutmut_6': xǁOAuthManagerǁrefresh_token__mutmut_6, 
        'xǁOAuthManagerǁrefresh_token__mutmut_7': xǁOAuthManagerǁrefresh_token__mutmut_7, 
        'xǁOAuthManagerǁrefresh_token__mutmut_8': xǁOAuthManagerǁrefresh_token__mutmut_8, 
        'xǁOAuthManagerǁrefresh_token__mutmut_9': xǁOAuthManagerǁrefresh_token__mutmut_9, 
        'xǁOAuthManagerǁrefresh_token__mutmut_10': xǁOAuthManagerǁrefresh_token__mutmut_10, 
        'xǁOAuthManagerǁrefresh_token__mutmut_11': xǁOAuthManagerǁrefresh_token__mutmut_11, 
        'xǁOAuthManagerǁrefresh_token__mutmut_12': xǁOAuthManagerǁrefresh_token__mutmut_12, 
        'xǁOAuthManagerǁrefresh_token__mutmut_13': xǁOAuthManagerǁrefresh_token__mutmut_13, 
        'xǁOAuthManagerǁrefresh_token__mutmut_14': xǁOAuthManagerǁrefresh_token__mutmut_14, 
        'xǁOAuthManagerǁrefresh_token__mutmut_15': xǁOAuthManagerǁrefresh_token__mutmut_15, 
        'xǁOAuthManagerǁrefresh_token__mutmut_16': xǁOAuthManagerǁrefresh_token__mutmut_16, 
        'xǁOAuthManagerǁrefresh_token__mutmut_17': xǁOAuthManagerǁrefresh_token__mutmut_17, 
        'xǁOAuthManagerǁrefresh_token__mutmut_18': xǁOAuthManagerǁrefresh_token__mutmut_18, 
        'xǁOAuthManagerǁrefresh_token__mutmut_19': xǁOAuthManagerǁrefresh_token__mutmut_19, 
        'xǁOAuthManagerǁrefresh_token__mutmut_20': xǁOAuthManagerǁrefresh_token__mutmut_20, 
        'xǁOAuthManagerǁrefresh_token__mutmut_21': xǁOAuthManagerǁrefresh_token__mutmut_21, 
        'xǁOAuthManagerǁrefresh_token__mutmut_22': xǁOAuthManagerǁrefresh_token__mutmut_22, 
        'xǁOAuthManagerǁrefresh_token__mutmut_23': xǁOAuthManagerǁrefresh_token__mutmut_23, 
        'xǁOAuthManagerǁrefresh_token__mutmut_24': xǁOAuthManagerǁrefresh_token__mutmut_24, 
        'xǁOAuthManagerǁrefresh_token__mutmut_25': xǁOAuthManagerǁrefresh_token__mutmut_25, 
        'xǁOAuthManagerǁrefresh_token__mutmut_26': xǁOAuthManagerǁrefresh_token__mutmut_26, 
        'xǁOAuthManagerǁrefresh_token__mutmut_27': xǁOAuthManagerǁrefresh_token__mutmut_27, 
        'xǁOAuthManagerǁrefresh_token__mutmut_28': xǁOAuthManagerǁrefresh_token__mutmut_28, 
        'xǁOAuthManagerǁrefresh_token__mutmut_29': xǁOAuthManagerǁrefresh_token__mutmut_29, 
        'xǁOAuthManagerǁrefresh_token__mutmut_30': xǁOAuthManagerǁrefresh_token__mutmut_30, 
        'xǁOAuthManagerǁrefresh_token__mutmut_31': xǁOAuthManagerǁrefresh_token__mutmut_31, 
        'xǁOAuthManagerǁrefresh_token__mutmut_32': xǁOAuthManagerǁrefresh_token__mutmut_32, 
        'xǁOAuthManagerǁrefresh_token__mutmut_33': xǁOAuthManagerǁrefresh_token__mutmut_33, 
        'xǁOAuthManagerǁrefresh_token__mutmut_34': xǁOAuthManagerǁrefresh_token__mutmut_34, 
        'xǁOAuthManagerǁrefresh_token__mutmut_35': xǁOAuthManagerǁrefresh_token__mutmut_35, 
        'xǁOAuthManagerǁrefresh_token__mutmut_36': xǁOAuthManagerǁrefresh_token__mutmut_36, 
        'xǁOAuthManagerǁrefresh_token__mutmut_37': xǁOAuthManagerǁrefresh_token__mutmut_37, 
        'xǁOAuthManagerǁrefresh_token__mutmut_38': xǁOAuthManagerǁrefresh_token__mutmut_38, 
        'xǁOAuthManagerǁrefresh_token__mutmut_39': xǁOAuthManagerǁrefresh_token__mutmut_39, 
        'xǁOAuthManagerǁrefresh_token__mutmut_40': xǁOAuthManagerǁrefresh_token__mutmut_40, 
        'xǁOAuthManagerǁrefresh_token__mutmut_41': xǁOAuthManagerǁrefresh_token__mutmut_41, 
        'xǁOAuthManagerǁrefresh_token__mutmut_42': xǁOAuthManagerǁrefresh_token__mutmut_42, 
        'xǁOAuthManagerǁrefresh_token__mutmut_43': xǁOAuthManagerǁrefresh_token__mutmut_43, 
        'xǁOAuthManagerǁrefresh_token__mutmut_44': xǁOAuthManagerǁrefresh_token__mutmut_44, 
        'xǁOAuthManagerǁrefresh_token__mutmut_45': xǁOAuthManagerǁrefresh_token__mutmut_45, 
        'xǁOAuthManagerǁrefresh_token__mutmut_46': xǁOAuthManagerǁrefresh_token__mutmut_46, 
        'xǁOAuthManagerǁrefresh_token__mutmut_47': xǁOAuthManagerǁrefresh_token__mutmut_47, 
        'xǁOAuthManagerǁrefresh_token__mutmut_48': xǁOAuthManagerǁrefresh_token__mutmut_48, 
        'xǁOAuthManagerǁrefresh_token__mutmut_49': xǁOAuthManagerǁrefresh_token__mutmut_49, 
        'xǁOAuthManagerǁrefresh_token__mutmut_50': xǁOAuthManagerǁrefresh_token__mutmut_50, 
        'xǁOAuthManagerǁrefresh_token__mutmut_51': xǁOAuthManagerǁrefresh_token__mutmut_51, 
        'xǁOAuthManagerǁrefresh_token__mutmut_52': xǁOAuthManagerǁrefresh_token__mutmut_52, 
        'xǁOAuthManagerǁrefresh_token__mutmut_53': xǁOAuthManagerǁrefresh_token__mutmut_53, 
        'xǁOAuthManagerǁrefresh_token__mutmut_54': xǁOAuthManagerǁrefresh_token__mutmut_54, 
        'xǁOAuthManagerǁrefresh_token__mutmut_55': xǁOAuthManagerǁrefresh_token__mutmut_55, 
        'xǁOAuthManagerǁrefresh_token__mutmut_56': xǁOAuthManagerǁrefresh_token__mutmut_56, 
        'xǁOAuthManagerǁrefresh_token__mutmut_57': xǁOAuthManagerǁrefresh_token__mutmut_57, 
        'xǁOAuthManagerǁrefresh_token__mutmut_58': xǁOAuthManagerǁrefresh_token__mutmut_58, 
        'xǁOAuthManagerǁrefresh_token__mutmut_59': xǁOAuthManagerǁrefresh_token__mutmut_59, 
        'xǁOAuthManagerǁrefresh_token__mutmut_60': xǁOAuthManagerǁrefresh_token__mutmut_60, 
        'xǁOAuthManagerǁrefresh_token__mutmut_61': xǁOAuthManagerǁrefresh_token__mutmut_61, 
        'xǁOAuthManagerǁrefresh_token__mutmut_62': xǁOAuthManagerǁrefresh_token__mutmut_62, 
        'xǁOAuthManagerǁrefresh_token__mutmut_63': xǁOAuthManagerǁrefresh_token__mutmut_63, 
        'xǁOAuthManagerǁrefresh_token__mutmut_64': xǁOAuthManagerǁrefresh_token__mutmut_64, 
        'xǁOAuthManagerǁrefresh_token__mutmut_65': xǁOAuthManagerǁrefresh_token__mutmut_65, 
        'xǁOAuthManagerǁrefresh_token__mutmut_66': xǁOAuthManagerǁrefresh_token__mutmut_66, 
        'xǁOAuthManagerǁrefresh_token__mutmut_67': xǁOAuthManagerǁrefresh_token__mutmut_67, 
        'xǁOAuthManagerǁrefresh_token__mutmut_68': xǁOAuthManagerǁrefresh_token__mutmut_68, 
        'xǁOAuthManagerǁrefresh_token__mutmut_69': xǁOAuthManagerǁrefresh_token__mutmut_69, 
        'xǁOAuthManagerǁrefresh_token__mutmut_70': xǁOAuthManagerǁrefresh_token__mutmut_70, 
        'xǁOAuthManagerǁrefresh_token__mutmut_71': xǁOAuthManagerǁrefresh_token__mutmut_71, 
        'xǁOAuthManagerǁrefresh_token__mutmut_72': xǁOAuthManagerǁrefresh_token__mutmut_72, 
        'xǁOAuthManagerǁrefresh_token__mutmut_73': xǁOAuthManagerǁrefresh_token__mutmut_73, 
        'xǁOAuthManagerǁrefresh_token__mutmut_74': xǁOAuthManagerǁrefresh_token__mutmut_74, 
        'xǁOAuthManagerǁrefresh_token__mutmut_75': xǁOAuthManagerǁrefresh_token__mutmut_75, 
        'xǁOAuthManagerǁrefresh_token__mutmut_76': xǁOAuthManagerǁrefresh_token__mutmut_76, 
        'xǁOAuthManagerǁrefresh_token__mutmut_77': xǁOAuthManagerǁrefresh_token__mutmut_77, 
        'xǁOAuthManagerǁrefresh_token__mutmut_78': xǁOAuthManagerǁrefresh_token__mutmut_78, 
        'xǁOAuthManagerǁrefresh_token__mutmut_79': xǁOAuthManagerǁrefresh_token__mutmut_79, 
        'xǁOAuthManagerǁrefresh_token__mutmut_80': xǁOAuthManagerǁrefresh_token__mutmut_80, 
        'xǁOAuthManagerǁrefresh_token__mutmut_81': xǁOAuthManagerǁrefresh_token__mutmut_81, 
        'xǁOAuthManagerǁrefresh_token__mutmut_82': xǁOAuthManagerǁrefresh_token__mutmut_82, 
        'xǁOAuthManagerǁrefresh_token__mutmut_83': xǁOAuthManagerǁrefresh_token__mutmut_83, 
        'xǁOAuthManagerǁrefresh_token__mutmut_84': xǁOAuthManagerǁrefresh_token__mutmut_84, 
        'xǁOAuthManagerǁrefresh_token__mutmut_85': xǁOAuthManagerǁrefresh_token__mutmut_85, 
        'xǁOAuthManagerǁrefresh_token__mutmut_86': xǁOAuthManagerǁrefresh_token__mutmut_86, 
        'xǁOAuthManagerǁrefresh_token__mutmut_87': xǁOAuthManagerǁrefresh_token__mutmut_87, 
        'xǁOAuthManagerǁrefresh_token__mutmut_88': xǁOAuthManagerǁrefresh_token__mutmut_88
    }
    
    def refresh_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁrefresh_token__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁrefresh_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    refresh_token.__signature__ = _mutmut_signature(xǁOAuthManagerǁrefresh_token__mutmut_orig)
    xǁOAuthManagerǁrefresh_token__mutmut_orig.__name__ = 'xǁOAuthManagerǁrefresh_token'
    
    def xǁOAuthManagerǁget_github_user__mutmut_orig(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_1(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = None
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_2(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'XXAuthorizationXX': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_3(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_4(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'AUTHORIZATION': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_5(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'XXAcceptXX': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_6(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_7(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'ACCEPT': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_8(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'XXapplication/vnd.github+jsonXX',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_9(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'APPLICATION/VND.GITHUB+JSON',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_10(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'XXX-GitHub-Api-VersionXX': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_11(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'x-github-api-version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_12(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GITHUB-API-VERSION': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_13(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': 'XX2022-11-28XX',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_14(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_15(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    None,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_16(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=None,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_17(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=None,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_18(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_19(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_20(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_21(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=31.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_22(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = None
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_23(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(None)
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_24(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(None)}")
            raise ValueError(error_msg)
    
    def xǁOAuthManagerǁget_github_user__mutmut_25(self, access_token: str) -> Dict:
        """
        Get GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
        
        Returns:
            User information dictionary
        
        Raises:
            ValueError: If request fails
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.GITHUB_API_URL}/user",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = sanitize_log_message(f"GitHub API request failed: {str(e)}")
            raise ValueError(None)
    
    xǁOAuthManagerǁget_github_user__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁget_github_user__mutmut_1': xǁOAuthManagerǁget_github_user__mutmut_1, 
        'xǁOAuthManagerǁget_github_user__mutmut_2': xǁOAuthManagerǁget_github_user__mutmut_2, 
        'xǁOAuthManagerǁget_github_user__mutmut_3': xǁOAuthManagerǁget_github_user__mutmut_3, 
        'xǁOAuthManagerǁget_github_user__mutmut_4': xǁOAuthManagerǁget_github_user__mutmut_4, 
        'xǁOAuthManagerǁget_github_user__mutmut_5': xǁOAuthManagerǁget_github_user__mutmut_5, 
        'xǁOAuthManagerǁget_github_user__mutmut_6': xǁOAuthManagerǁget_github_user__mutmut_6, 
        'xǁOAuthManagerǁget_github_user__mutmut_7': xǁOAuthManagerǁget_github_user__mutmut_7, 
        'xǁOAuthManagerǁget_github_user__mutmut_8': xǁOAuthManagerǁget_github_user__mutmut_8, 
        'xǁOAuthManagerǁget_github_user__mutmut_9': xǁOAuthManagerǁget_github_user__mutmut_9, 
        'xǁOAuthManagerǁget_github_user__mutmut_10': xǁOAuthManagerǁget_github_user__mutmut_10, 
        'xǁOAuthManagerǁget_github_user__mutmut_11': xǁOAuthManagerǁget_github_user__mutmut_11, 
        'xǁOAuthManagerǁget_github_user__mutmut_12': xǁOAuthManagerǁget_github_user__mutmut_12, 
        'xǁOAuthManagerǁget_github_user__mutmut_13': xǁOAuthManagerǁget_github_user__mutmut_13, 
        'xǁOAuthManagerǁget_github_user__mutmut_14': xǁOAuthManagerǁget_github_user__mutmut_14, 
        'xǁOAuthManagerǁget_github_user__mutmut_15': xǁOAuthManagerǁget_github_user__mutmut_15, 
        'xǁOAuthManagerǁget_github_user__mutmut_16': xǁOAuthManagerǁget_github_user__mutmut_16, 
        'xǁOAuthManagerǁget_github_user__mutmut_17': xǁOAuthManagerǁget_github_user__mutmut_17, 
        'xǁOAuthManagerǁget_github_user__mutmut_18': xǁOAuthManagerǁget_github_user__mutmut_18, 
        'xǁOAuthManagerǁget_github_user__mutmut_19': xǁOAuthManagerǁget_github_user__mutmut_19, 
        'xǁOAuthManagerǁget_github_user__mutmut_20': xǁOAuthManagerǁget_github_user__mutmut_20, 
        'xǁOAuthManagerǁget_github_user__mutmut_21': xǁOAuthManagerǁget_github_user__mutmut_21, 
        'xǁOAuthManagerǁget_github_user__mutmut_22': xǁOAuthManagerǁget_github_user__mutmut_22, 
        'xǁOAuthManagerǁget_github_user__mutmut_23': xǁOAuthManagerǁget_github_user__mutmut_23, 
        'xǁOAuthManagerǁget_github_user__mutmut_24': xǁOAuthManagerǁget_github_user__mutmut_24, 
        'xǁOAuthManagerǁget_github_user__mutmut_25': xǁOAuthManagerǁget_github_user__mutmut_25
    }
    
    def get_github_user(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁget_github_user__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁget_github_user__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_github_user.__signature__ = _mutmut_signature(xǁOAuthManagerǁget_github_user__mutmut_orig)
    xǁOAuthManagerǁget_github_user__mutmut_orig.__name__ = 'xǁOAuthManagerǁget_github_user'
    
    def xǁOAuthManagerǁrevoke_token__mutmut_orig(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
        """
        Revoke an access token.
        
        Note: GitHub doesn't have a standard token revocation endpoint,
        so this marks the token as revoked locally.
        
        Args:
            access_token: Token to revoke
            config: OAuth configuration
        
        Returns:
            True if revocation successful
        """
        # For GitHub, we can delete the OAuth app authorization
        # This would require a different endpoint and app permissions
        # For now, just remove from local storage
        
        # Find and remove token from storage
        for token_id, token in list(self._token_store.items()):
            if token.access_token == access_token:
                del self._token_store[token_id]
                return True
        
        return False
    
    def xǁOAuthManagerǁrevoke_token__mutmut_1(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
        """
        Revoke an access token.
        
        Note: GitHub doesn't have a standard token revocation endpoint,
        so this marks the token as revoked locally.
        
        Args:
            access_token: Token to revoke
            config: OAuth configuration
        
        Returns:
            True if revocation successful
        """
        # For GitHub, we can delete the OAuth app authorization
        # This would require a different endpoint and app permissions
        # For now, just remove from local storage
        
        # Find and remove token from storage
        for token_id, token in list(None):
            if token.access_token == access_token:
                del self._token_store[token_id]
                return True
        
        return False
    
    def xǁOAuthManagerǁrevoke_token__mutmut_2(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
        """
        Revoke an access token.
        
        Note: GitHub doesn't have a standard token revocation endpoint,
        so this marks the token as revoked locally.
        
        Args:
            access_token: Token to revoke
            config: OAuth configuration
        
        Returns:
            True if revocation successful
        """
        # For GitHub, we can delete the OAuth app authorization
        # This would require a different endpoint and app permissions
        # For now, just remove from local storage
        
        # Find and remove token from storage
        for token_id, token in list(self._token_store.items()):
            if token.access_token != access_token:
                del self._token_store[token_id]
                return True
        
        return False
    
    def xǁOAuthManagerǁrevoke_token__mutmut_3(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
        """
        Revoke an access token.
        
        Note: GitHub doesn't have a standard token revocation endpoint,
        so this marks the token as revoked locally.
        
        Args:
            access_token: Token to revoke
            config: OAuth configuration
        
        Returns:
            True if revocation successful
        """
        # For GitHub, we can delete the OAuth app authorization
        # This would require a different endpoint and app permissions
        # For now, just remove from local storage
        
        # Find and remove token from storage
        for token_id, token in list(self._token_store.items()):
            if token.access_token == access_token:
                del self._token_store[token_id]
                return False
        
        return False
    
    def xǁOAuthManagerǁrevoke_token__mutmut_4(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
        """
        Revoke an access token.
        
        Note: GitHub doesn't have a standard token revocation endpoint,
        so this marks the token as revoked locally.
        
        Args:
            access_token: Token to revoke
            config: OAuth configuration
        
        Returns:
            True if revocation successful
        """
        # For GitHub, we can delete the OAuth app authorization
        # This would require a different endpoint and app permissions
        # For now, just remove from local storage
        
        # Find and remove token from storage
        for token_id, token in list(self._token_store.items()):
            if token.access_token == access_token:
                del self._token_store[token_id]
                return True
        
        return True
    
    xǁOAuthManagerǁrevoke_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthManagerǁrevoke_token__mutmut_1': xǁOAuthManagerǁrevoke_token__mutmut_1, 
        'xǁOAuthManagerǁrevoke_token__mutmut_2': xǁOAuthManagerǁrevoke_token__mutmut_2, 
        'xǁOAuthManagerǁrevoke_token__mutmut_3': xǁOAuthManagerǁrevoke_token__mutmut_3, 
        'xǁOAuthManagerǁrevoke_token__mutmut_4': xǁOAuthManagerǁrevoke_token__mutmut_4
    }
    
    def revoke_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthManagerǁrevoke_token__mutmut_orig"), object.__getattribute__(self, "xǁOAuthManagerǁrevoke_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    revoke_token.__signature__ = _mutmut_signature(xǁOAuthManagerǁrevoke_token__mutmut_orig)
    xǁOAuthManagerǁrevoke_token__mutmut_orig.__name__ = 'xǁOAuthManagerǁrevoke_token'
