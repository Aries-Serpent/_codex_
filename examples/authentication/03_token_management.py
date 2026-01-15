#!/usr/bin/env python3
"""
Example: Token Management and Session Handling

This script demonstrates generating, validating, and managing
access tokens, refresh tokens, and sessions.

⚠️  SECURITY WARNING - DEMONSTRATION ONLY:
    This example displays partial tokens for educational purposes.
    In production environments:
    - NEVER log tokens to console, files, or logging systems
    - Store tokens in httpOnly cookies or encrypted storage
    - Use secure, encrypted channels for token transmission
    - Implement proper token rotation and revocation
    - Follow OWASP guidelines for session management

Usage:
    python examples/authentication/03_token_management.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.codex.auth.token_manager import TokenManager, TokenType


def main():
    """Run token management demo."""
    
    print("=" * 60)
    print("Token Management and Session Handling Example")
    print("=" * 60)
    
    # Initialize token manager with a secret key
    # In production, load from environment variable
    secret_key = "demo_secret_key_do_not_use_in_production"
    tokens = TokenManager(secret_key=secret_key)
    
    user_id = "demo_user_123"
    
    # Step 1: Generate Access Token
    print("\n🔐 Step 1: Generate Access Token")
    print("-" * 60)
    
    access_token = tokens.generate_access_token(
        user_id=user_id,
        scope="repo user"
    )
    
    print(f"✓ Access token generated")
    print(f"  Token (first 40 chars): {access_token[:40]}...")
    print(f"  Expiry: 15 minutes")
    print(f"  Use: API requests")
    
    # Step 2: Validate Access Token
    print("\n🔐 Step 2: Validate Access Token")
    print("-" * 60)
    
    try:
        claims = tokens.validate_token(access_token, TokenType.ACCESS)
        print(f"✓ Token is valid")
        print(f"  User ID: {claims.sub}")
        print(f"  Type: {claims.type.value}")
        print(f"  Scope: {claims.scope}")
        print(f"  Issued at: {claims.iat}")
        print(f"  Expires at: {claims.exp}")
        print(f"  Issuer: {claims.iss}")
        print(f"  Audience: {claims.aud}")
    except ValueError as e:
        print(f"✗ Token validation failed: {e}")
    
    # Step 3: Generate Refresh Token
    print("\n🔐 Step 3: Generate Refresh Token")
    print("-" * 60)
    
    refresh_token = tokens.generate_refresh_token(user_id)
    
    print(f"\n✓ Refresh token generated")
    print(f"  Token length: {len(refresh_token)} characters")
    print(f"  [DEMO] First 20 chars: {refresh_token[:20]}...")
    print(f"  Expiry: 7 days")
    print(f"  Use: Refresh expired access tokens")
    print(f"\n⚠️  Production: Store refresh tokens securely!")
    
    # Step 4: Refresh Access Token
    print("\n🔐 Step 4: Refresh Access Token")
    print("-" * 60)
    
    try:
        new_access_token = tokens.refresh_access_token(refresh_token)
        print(f"\n✓ Access token refreshed")
        print(f"  New token length: {len(new_access_token)} characters")
        print(f"  [DEMO] First 20 chars: {new_access_token[:20]}...")
        
        # Validate new token
        new_claims = tokens.validate_token(new_access_token, TokenType.ACCESS)
        print(f"  User ID: {new_claims.sub}")
        print(f"\n⚠️  Production: Secure token refresh critical for security!")
    except ValueError as e:
        print(f"✗ Refresh failed: {e}")
    
    # Step 5: Generate Session Token
    print("\n🔐 Step 5: Generate Session Token")
    print("-" * 60)
    
    session_token, session_id = tokens.generate_session_token(
        user_id=user_id,
        mfa_verified=True,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Example Browser)"
    )
    
    print(f"\n✓ Session created")
    print(f"  Session ID: {session_id[:16]}...{session_id[-8:]}")
    print(f"  Token length: {len(session_token)} characters")
    print(f"  [DEMO] First 20 chars: {session_token[:20]}...")
    print(f"  Expiry: 30 days (with inactivity timeout)")
    print(f"\n⚠️  Production: Sessions must be stored securely with encryption!")
    
    # Step 6: Get Session Information
    print("\n🔐 Step 6: Get Session Information")
    print("-" * 60)
    
    session = tokens.get_session(session_id)
    if session:
        print(f"✓ Session found")
        print(f"  Session ID: {session.session_id}")
        print(f"  User ID: {session.user_id}")
        print(f"  Created: {time.ctime(session.created_at)}")
        print(f"  Last activity: {time.ctime(session.last_activity)}")
        print(f"  MFA verified: {'Yes' if session.mfa_verified else 'No'}")
        print(f"  IP address: {session.ip_address}")
        print(f"  User agent: {session.user_agent}")
        print(f"  Active: {'Yes' if session.is_active() else 'No'}")
    
    # Step 7: Create Multiple Sessions
    print("\n🔐 Step 7: Create Multiple Sessions")
    print("-" * 60)
    
    tokens.generate_session_token(
        user_id=user_id,
        mfa_verified=True,
        ip_address="192.168.1.101",
        user_agent="Mobile App"
    )
    
    tokens.generate_session_token(
        user_id=user_id,
        mfa_verified=False,
        ip_address="192.168.1.102",
        user_agent="Desktop App"
    )
    
    print(f"✓ Created 2 additional sessions")
    
    # List all user sessions
    user_sessions = tokens.get_user_sessions(user_id)
    print(f"\nActive sessions for user {user_id}: {len(user_sessions)}")
    for i, sess in enumerate(user_sessions, 1):
        print(f"\n  Session {i}:")
        print(f"    ID: {sess.session_id[:16]}...")
        print(f"    IP: {sess.ip_address}")
        print(f"    MFA: {'Yes' if sess.mfa_verified else 'No'}")
        print(f"    Agent: {sess.user_agent[:30]}...")
    
    # Step 8: Token Revocation
    print("\n🔐 Step 8: Token Revocation")
    print("-" * 60)
    
    # Revoke a single token
    print("\nRevoking access token...")
    result = tokens.revoke_token(access_token)
    print(f"✓ Token revoked: {result}")
    
    # Try to validate revoked token
    try:
        tokens.validate_token(access_token)
        print("✗ Token still valid (unexpected)")
    except ValueError as e:
        print(f"✓ Token correctly rejected: {str(e)[:50]}...")
    
    # Revoke all user sessions
    print(f"\nRevoking all sessions for user {user_id}...")
    count = tokens.revoke_all_user_tokens(user_id)
    print(f"✓ Revoked {count} sessions")
    
    # Verify sessions are gone
    remaining_sessions = tokens.get_user_sessions(user_id)
    print(f"Remaining sessions: {len(remaining_sessions)}")
    
    # Step 9: Session Cleanup
    print("\n🔐 Step 9: Session Cleanup")
    print("-" * 60)
    
    # Create an expired session for testing
    print("\nCreating test expired session...")
    old_session_token, old_session_id = tokens.generate_session_token(
        user_id="test_user",
        mfa_verified=False
    )
    
    # Manually expire it
    old_session = tokens.get_session(old_session_id)
    if old_session:
        old_session.last_activity = time.time() - 2000  # 33+ minutes ago
    
    print("✓ Created expired session")
    
    # Clean up
    print("\nRunning cleanup...")
    cleaned = tokens.cleanup_expired_sessions()
    print(f"✓ Cleaned up {cleaned} expired sessions")
    
    # Summary
    print("\n" + "=" * 60)
    print("Token Management Summary")
    print("=" * 60)
    
    print("\n✓ Access Tokens:")
    print("  - Short-lived (15 minutes)")
    print("  - Used for API requests")
    print("  - Can be refreshed")
    
    print("\n✓ Refresh Tokens:")
    print("  - Long-lived (7 days)")
    print("  - Used to get new access tokens")
    print("  - Should be stored securely")
    
    print("\n✓ Session Tokens:")
    print("  - Very long-lived (30 days)")
    print("  - Track user activity")
    print("  - Support MFA verification")
    print("  - Include device information")
    
    print("\n✓ Security Features:")
    print("  - HMAC-SHA256 signatures")
    print("  - Token expiry validation")
    print("  - Token revocation lists")
    print("  - Session activity tracking")
    print("  - Automatic cleanup")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
