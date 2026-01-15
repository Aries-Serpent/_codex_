"""
Authentication module for Codex platform.

Provides OAuth2 authentication, MFA, and token management
with a focus on GitHub-owned services.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .oauth_manager import OAuthManager
    from .mfa_provider import MFAProvider
    from .token_manager import TokenManager

__all__ = [
    "OAuthManager",
    "MFAProvider",
    "TokenManager",
]
