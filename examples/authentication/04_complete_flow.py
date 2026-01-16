#!/usr/bin/env python3
"""
Example: Complete Authentication Flow

This script demonstrates a complete authentication flow combining:
- GitHub OAuth
- Multi-Factor Authentication
- Token Management
- Session Handling

⚠️  SECURITY WARNING - DEMONSTRATION ONLY:
    This example displays sensitive data (tokens, secrets, session IDs) to console
    for educational purposes. In production environments:
    - NEVER log tokens, secrets, or sensitive session data
    - Store tokens in httpOnly cookies or secure storage only
    - Use encrypted channels for all sensitive data transmission
    - Implement proper secret management (AWS KMS, HashiCorp Vault)
    - Follow OWASP guidelines for authentication security

Usage:
    1. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET
    2. Run: python examples/authentication/04_complete_flow.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.codex.auth import OAuthManager, MFAProvider, TokenManager


class AuthenticationDemo:
    """Complete authentication flow demonstration."""
    
    def __init__(self):
        """Initialize authentication components."""
        self.oauth = OAuthManager()
        self.mfa = MFAProvider()
        self.tokens = TokenManager(secret_key=os.getenv('TOKEN_SECRET_KEY', 'demo_key'))
        
    def github_login(self) -> dict:
        """Perform GitHub OAuth login."""
        print("\n" + "=" * 60)
        print("GITHUB AUTHENTICATION")
        print("=" * 60)
        
        # Configure GitHub OAuth
        config = self.oauth.create_github_config(
            client_id=os.getenv('GITHUB_CLIENT_ID', 'demo_id'),
            client_secret=os.getenv('GITHUB_CLIENT_SECRET', 'demo_secret'),
            redirect_uri=os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:8000/callback'),
            scope="repo user"
        )
        
        # Initiate OAuth flow
        flow = self.oauth.initiate_flow(config)
        print(f"\n👉 Visit: {flow['auth_url']}")
        
        # In a real application, this would be handled by a web server
        # For demo purposes, we simulate getting the code
        print("\n⚠️  DEMO MODE: Simulating OAuth flow")
        print("In production, user would visit URL and authorize")
        
        return {
            'user_id': 'demo_user_123',
            'username': 'demo_user',
            'email': 'demo@example.com',
            'name': 'Demo User'
        }
    
    def setup_mfa(self, user_id: str) -> dict:
        """
        Setup MFA for user.
        
        SECURITY WARNING: This demo displays sensitive MFA secrets and backup codes.
        In production, secrets must be transmitted through secure, authenticated channels only.
        """
        print("\n" + "=" * 60)
        print("MULTI-FACTOR AUTHENTICATION SETUP")
        print("=" * 60)
        
        print("\n⚠️  DEMO MODE: Displaying sensitive secrets (never do this in production!)")
        
        # Generate TOTP secret
        secret = self.mfa.generate_totp_secret(user_id, issuer="Codex")
        
        # Get provisioning URI for QR code
        uri = secret.get_provisioning_uri("user@example.com")
        
        print(f"\n✓ MFA secret generated")
        print(f"\n📱 Setup URL:")
        # In production: Generate QR code image, display in secure authenticated portal
        print(f"[DEMO ONLY - PARTIAL]: {uri[:60]}...")
        
        # Generate backup codes
        backup_codes = self.mfa.generate_backup_codes(user_id, count=10)
        
        print(f"\n📋 Backup Codes:")
        # In production: Display once in secure authenticated portal, require acknowledgment
        for i, code in enumerate(backup_codes, 1):
            print(f"  {i:2d}. [DEMO] {code}")
        
        print("\n⚠️  Production Security Requirements:")
        print("   - Display secrets only in authenticated, encrypted sessions")
        print("   - Never log secrets to console, files, or logging systems")
        print("   - Use secure delivery methods (encrypted email, secure portal)")
        print("   - Require user acknowledgment before closing setup screen")
        
        return {
            'secret': secret.secret,
            'backup_codes': backup_codes,
            'remaining_codes': self.mfa.get_remaining_backup_codes(user_id)
        }
    
    def verify_mfa(self, user_id: str, secret: str) -> bool:
        """Verify MFA code."""
        print("\n" + "=" * 60)
        print("MFA VERIFICATION")
        print("=" * 60)
        
        # Generate a test code for demo
        test_code = self.mfa.generate_totp(secret)
        
        print(f"\n🔐 DEMO: Generated code: {test_code}")
        print("In production, user would enter code from their app")
        
        # Verify the code
        is_valid = self.mfa.verify_totp(secret, test_code, user_id)
        
        if is_valid:
            print("✓ MFA verification successful")
        else:
            print("✗ MFA verification failed")
        
        return is_valid
    
    def create_session(self, user_id: str, mfa_verified: bool) -> dict:
        """
        Create authenticated session.
        
        SECURITY WARNING: This demo displays token prefixes and session IDs.
        In production, tokens should NEVER be logged. Use secure storage only.
        """
        print("\n" + "=" * 60)
        print("SESSION CREATION")
        print("=" * 60)
        
        # Generate tokens
        # PRODUCTION WARNING: The hardcoded IP address and user agent below are for
        # demonstration purposes only. In a real production implementation:
        #
        # 1. Extract the actual client IP from the HTTP request headers:
        #    - X-Forwarded-For (if behind proxy/load balancer)
        #    - X-Real-IP (if behind reverse proxy)
        #    - request.remote_addr (direct connection)
        #
        # 2. Extract the actual user agent from HTTP request headers:
        #    - User-Agent header from the request
        #
        # 3. Use these real values for session security and audit trails:
        #    - Session hijacking detection (IP change alerts)
        #    - Device fingerprinting and anomaly detection
        #    - Audit logs for security investigations
        #    - Compliance reporting (access from which locations/devices)
        #
        # Example (Flask):
        #   ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        #   user_agent = request.headers.get('User-Agent', 'Unknown')
        #
        # Example (FastAPI):
        #   ip_address = request.client.host
        #   user_agent = request.headers.get('user-agent', 'Unknown')
        #
        access_token = self.tokens.generate_access_token(user_id, scope="repo user")
        refresh_token = self.tokens.generate_refresh_token(user_id)
        session_token, session_id = self.tokens.generate_session_token(
            user_id=user_id,
            mfa_verified=mfa_verified,
            ip_address="192.168.1.100",  # DEMO ONLY - Use real client IP in production
            user_agent="Demo Client"      # DEMO ONLY - Use real user agent in production
        )
        
        print(f"\n✓ Tokens generated:")
        # Production: NEVER log tokens. Store securely in httpOnly cookies or secure storage
        print(f"  Access token: [REDACTED - {len(access_token)} chars]")
        print(f"  Refresh token: [REDACTED - {len(refresh_token)} chars]")
        print(f"  Session token: [REDACTED - {len(session_token)} chars]")
        print(f"  Session ID: {session_id[:16]}...{session_id[-8:]}")
        
        # Get session info
        session = self.tokens.get_session(session_id)
        if session:
            print(f"\n✓ Session details:")
            print(f"  User: {session.user_id}")
            print("  MFA status: [REDACTED]")
            print(f"  IP: {session.ip_address}")
            print(f"  Active: {session.is_active()}")
        
        print("\n⚠️  Production: Never log tokens or sensitive session data!")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_token': session_token,
            'session_id': session_id
        }
    
    def run_complete_flow(self):
        """Run complete authentication flow."""
        print("=" * 60)
        print("COMPLETE AUTHENTICATION FLOW DEMO")
        print("=" * 60)
        
        # Step 1: GitHub OAuth Login
        user_data = self.github_login()
        user_id = user_data['user_id']
        
        print(f"\n✓ Step 1: GitHub login successful")
        print(f"  User: {user_data['username']}")
        print(f"  Email: {user_data['email']}")
        
        # Step 2: Setup MFA (first time users)
        mfa_data = self.setup_mfa(user_id)
        
        print(f"\n✓ Step 2: MFA setup complete")
        print(f"  Secret generated: Yes")
        print("  Backup codes: [redacted, generated successfully]")
        print(f"  ⚠️  Secret data secured (not logged in production)")
        
        # Step 3: Verify MFA
        mfa_verified = self.verify_mfa(user_id, mfa_data['secret'])
        
        print(f"\n✓ Step 3: MFA verification {'passed' if mfa_verified else 'failed'}")
        
        # Step 4: Create Session
        session_data = self.create_session(user_id, mfa_verified)
        
        print(f"\n✓ Step 4: Session created")
        print(f"  Session ID: {session_data['session_id']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("AUTHENTICATION COMPLETE")
        print("=" * 60)
        
        print(f"\n✅ User authenticated successfully!")
        print(f"\n📝 Authentication Summary:")
        print(f"  ✓ GitHub OAuth: Completed")
        print(f"  ✓ MFA Setup: Completed")
        print(f"  ✓ MFA Verified: {'Yes' if mfa_verified else 'No'}")
        print(f"  ✓ Session Created: Yes")
        print(f"  ✓ Tokens Issued: 3 (access, refresh, session)")
        
        print(f"\n🔒 Security Features Active:")
        print(f"  ✓ OAuth2 with PKCE")
        print(f"  ✓ TOTP-based MFA")
        print(f"  ✓ Rate limiting")
        print(f"  ✓ Token expiry")
        print(f"  ✓ Session tracking")
        
        print(f"\n📊 Session Details:")
        print(f"  User ID: {user_id}")
        print(f"  Session ID: {session_data['session_id']}")
        print(f"  MFA Status: {'Verified' if mfa_verified else 'Not Verified'}")
        
        return session_data


def main():
    """Run the demo."""
    demo = AuthenticationDemo()
    demo.run_complete_flow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
