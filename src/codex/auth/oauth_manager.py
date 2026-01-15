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
    
    def __init__(self, config: Optional[OAuthConfig] = None):
        """
        Initialize OAuth manager.
        
        Args:
            config: Optional OAuth configuration. If not provided, will use GitHub defaults.
        """
        self.config = config
        self._state_store: Dict[str, Dict] = {}  # In-memory state storage (use Redis in production)
        self._token_store: Dict[str, OAuthToken] = {}  # In-memory token storage (use database in production)
        
    def create_github_config(self, client_id: str, client_secret: Optional[str], 
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
    
    def _generate_state(self) -> str:
        """Generate secure random state for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(64)
    
    def _generate_code_challenge(self, verifier: str) -> str:
        """
        Generate PKCE code challenge from verifier.
        
        Uses S256 method (SHA-256 hash).
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        # Base64 URL-safe encoding without padding
        challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        return challenge
    
    def initiate_flow(self, config: Optional[OAuthConfig] = None) -> Dict[str, str]:
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
    
    def validate_state(self, state: str) -> bool:
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
    
    def exchange_code(self, code: str, state: str) -> OAuthToken:
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
    
    def refresh_token(self, refresh_token: str, config: Optional[OAuthConfig] = None) -> OAuthToken:
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
    
    def get_github_user(self, access_token: str) -> Dict:
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
    
    def revoke_token(self, access_token: str, config: Optional[OAuthConfig] = None) -> bool:
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
