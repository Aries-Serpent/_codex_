#!/usr/bin/env python3
"""
Example: Complete GitHub OAuth Authentication Flow

This script demonstrates the complete OAuth2 authentication flow
with GitHub using the Codex authentication system.

⚠️  SECURITY WARNING - DEMONSTRATION ONLY:
    This example shows partial tokens for educational purposes.
    In production environments:
    - NEVER log or display tokens (even partially)
    - Store tokens in httpOnly cookies or secure storage
    - Use encrypted channels for all token transmission
    - Implement proper token lifecycle management
    - Follow OWASP guidelines for OAuth security

Usage:
    1. Set up environment variables (see .env.example)
    2. Run: python examples/authentication/01_oauth_flow.py
    3. Follow the prompts to authenticate
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.codex.auth.oauth_manager import OAuthManager


def main():
    """Run GitHub OAuth authentication flow."""
    
    print("=" * 60)
    print("GitHub OAuth Authentication Example")
    print("=" * 60)
    
    # Check environment variables
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    redirect_uri = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:8000/callback')
    
    if not client_id or not client_secret:
        print("\n❌ Error: Missing environment variables!")
        print("\nPlease set:")
        print("  GITHUB_CLIENT_ID")
        print("  GITHUB_CLIENT_SECRET")
        print("  GITHUB_REDIRECT_URI (optional)")
        print("\nSee .env.example for details")
        return 1
    
    # Initialize OAuth manager
    oauth = OAuthManager()
    
    # Create GitHub configuration
    print("\n📝 Configuring GitHub OAuth...")
    config = oauth.create_github_config(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="repo user"
    )
    print(f"✓ Configured for redirect: {redirect_uri}")
    
    # Step 1: Initiate OAuth flow
    print("\n🔐 Initiating OAuth flow...")
    flow = oauth.initiate_flow(config)
    
    print("\n" + "=" * 60)
    print("STEP 1: Authorize Application")
    print("=" * 60)
    print(f"\n👉 Visit this URL in your browser:\n\n{flow['auth_url']}\n")
    print("After authorizing, you'll be redirected to your callback URL.")
    print("Copy the 'code' parameter from the URL.")
    
    # Step 2: Get authorization code from user
    print("\n" + "=" * 60)
    print("STEP 2: Enter Authorization Code")
    print("=" * 60)
    code = input("\nPaste the authorization code here: ").strip()
    
    if not code:
        print("❌ No code provided. Exiting.")
        return 1
    
    # Step 3: Exchange code for token
    print("\n🔄 Exchanging code for access token...")
    try:
        token = oauth.exchange_code(code, flow['state'])
        print("✓ Token obtained successfully!")
        
        print(f"\n📋 Token Details:")
        print(f"  Type: {token.token_type}")
        print(f"  Expires in: {token.expires_in} seconds")
        print(f"  Has refresh token: {'Yes' if token.refresh_token else 'No'}")
        print(f"  Scope: {token.scope}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Step 4: Get user information
    print("\n👤 Fetching user information...")
    try:
        user = oauth.get_github_user(token.access_token)
        
        print("\n" + "=" * 60)
        print("Authentication Successful!")
        print("=" * 60)
        print(f"\n✓ Authenticated as: {user['login']}")
        print(f"  Name: {user.get('name', 'N/A')}")
        print(f"  Email: {user.get('email', 'N/A')}")
        print(f"  Company: {user.get('company', 'N/A')}")
        print(f"  Profile: {user.get('html_url', 'N/A')}")
        print(f"  Public repos: {user.get('public_repos', 'N/A')}")
        print(f"  Followers: {user.get('followers', 'N/A')}")
        
        print("\n✅ OAuth flow completed successfully!")
        
        # Optional: Test token refresh if refresh token available
        if token.refresh_token:
            print("\n🔄 Testing token refresh...")
            try:
                new_token = oauth.refresh_token(token.refresh_token, config)
                print("✓ Token refresh successful!")
                print(f"  New token expires in: {new_token.expires_in} seconds")
            except ValueError as e:
                print(f"⚠ Token refresh note: {e}")
        
        return 0
        
    except ValueError as e:
        print(f"❌ Error fetching user info: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
