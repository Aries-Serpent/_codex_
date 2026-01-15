"""
Authentication module for Codex platform.

Provides OAuth2 authentication, MFA, and token management
with a focus on GitHub-owned services.
"""

from .oauth_manager import OAuthManager, OAuthToken, OAuthConfig
from .mfa_provider import MFAProvider, MFASecret, BackupCode
from .token_manager import TokenManager, TokenType, TokenClaims, SessionInfo

__all__ = [
    "OAuthManager",
    "OAuthToken",
    "OAuthConfig",
    "MFAProvider",
    "MFASecret",
    "BackupCode",
    "TokenManager",
    "TokenType",
    "TokenClaims",
    "SessionInfo",
]
