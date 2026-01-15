#!/usr/bin/env python3
"""
Example: Multi-Factor Authentication Setup and Verification

This script demonstrates setting up TOTP-based MFA with backup codes
and verifying authentication codes.

⚠️  SECURITY WARNING - DEMONSTRATION ONLY:
    This example displays sensitive secrets (TOTP keys, backup codes) to console
    for educational purposes. In production environments:
    - NEVER log or print secrets to console, logs, or files
    - Display secrets only in secure, authenticated web portals
    - Use encrypted channels (HTTPS, encrypted email) for secret transmission
    - Implement secure secret storage with encryption at rest
    - Follow OWASP guidelines for credential management

Usage:
    python examples/authentication/02_mfa_setup.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.codex.auth.mfa_provider import MFAProvider


def display_qr_instructions(uri: str, secret: str):
    """
    Display instructions for QR code setup.
    
    SECURITY WARNING: This is a demonstration script that displays sensitive
    TOTP secrets. In production, secrets should NEVER be logged or displayed
    in plain text. Use secure channels to transmit secrets to users.
    """
    print("\n" + "=" * 60)
    print("Setup Authenticator App")
    print("=" * 60)
    
    print("\n⚠️  SECURITY WARNING: This demo displays sensitive secrets.")
    print("    In production, use secure channels (encrypted email, secure portal).")
    
    print("\n📱 Option 1: Scan QR Code (Recommended)")
    print("-" * 60)
    print("Use a QR code generator with your TOTP provisioning URL.")
    # In production, generate QR code image and display securely.
    # Do NOT log or print the provisioning URI, as it embeds the secret key.
    print("\n[REDACTED] Provisioning URI generated (not displayed for security).\n")
    print("Or install qrcode library and generate QR code:")
    print("  pip install qrcode[pil]")
    print("  # Then use qrcode.make(uri) to generate image in a secure channel")
    
    print("\n✏️  Option 2: Manual Entry")
    print("-" * 60)
    # In production, display this through secure authenticated portal only.
    print("  Secret Key: [REDACTED - not displayed in logs or console]")
    print(f"  Account: user@example.com")
    print(f"  Type: Time-based")
    print(f"  Algorithm: SHA1")
    print(f"  Digits: 6")
    print(f"  Period: 30 seconds")
    print("\n⚠️  Production: Never log or print secrets in plain text!")


def main():
    """Run MFA setup and verification demo."""
    
    print("=" * 60)
    print("Multi-Factor Authentication (MFA) Setup Example")
    print("=" * 60)
    
    # Initialize MFA provider
    mfa = MFAProvider()
    
    # User identifier
    user_id = "demo_user_123"
    
    # Step 1: Generate TOTP secret
    print("\n🔐 Step 1: Generating TOTP Secret")
    print("-" * 60)
    
    secret = mfa.generate_totp_secret(user_id, issuer="Codex Demo")
    print(f"✓ Secret generated for user: {user_id}")
    
    # Step 2: Display setup instructions
    uri = secret.get_provisioning_uri("user@example.com")
    display_qr_instructions(uri, secret.secret)
    
    # Step 3: Verify setup
    print("\n🔐 Step 2: Verify Setup")
    print("-" * 60)
    print("\nEnter the 6-digit code from your authenticator app")
    print("(or press Enter to skip verification)")
    
    code = input("\nCode: ").strip()
    
    if code:
        is_valid = mfa.verify_totp(secret.secret, code, user_id)
        
        if is_valid:
            print("\n✅ SUCCESS! MFA setup verified!")
        else:
            print("\n❌ Invalid code. This could be due to:")
            print("  - Incorrect code entry")
            print("  - Time synchronization issues")
            print("  - Secret not properly added to app")
    else:
        print("\n⚠️  Skipping verification")
    
    # Step 4: Generate backup codes
    print("\n🔐 Step 3: Generate Backup Codes")
    print("-" * 60)
    
    backup_codes = mfa.generate_backup_codes(user_id, count=10)
    
    print("\n📋 BACKUP CODES (Save these securely!)")
    print("=" * 60)
    for i, backup_code in enumerate(backup_codes, 1):
        print(f"  {i:2d}. {backup_code}")
    print("=" * 60)
    print("\n⚠️  Important:")
    print("  - Each code can only be used ONCE")
    print("  - Store these in a secure location")
    print("  - Use if you lose access to your authenticator")
    
    remaining = mfa.get_remaining_backup_codes(user_id)
    print(f"\n✓ Generated {remaining} backup codes")
    
    # Step 5: Test TOTP verification
    print("\n🔐 Step 4: Test TOTP Verification")
    print("-" * 60)
    
    # Generate a code server-side for testing
    test_code = mfa.generate_totp(secret.secret)
    print(f"\nTest: Generated code {test_code} (valid for ~30 seconds)")
    
    # Wait a moment to show time-based nature
    time.sleep(2)
    
    is_valid = mfa.verify_totp(secret.secret, test_code, user_id)
    print(f"Verification result: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Step 6: Test backup code
    print("\n🔐 Step 5: Test Backup Code")
    print("-" * 60)
    
    test_backup = backup_codes[0]
    print(f"\nTesting backup code: {test_backup}")
    
    is_valid = mfa.verify_backup_code(user_id, test_backup)
    print(f"Verification result: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    if is_valid:
        remaining = mfa.get_remaining_backup_codes(user_id)
        print(f"Remaining codes: {remaining}")
        
        # Try using the same code again
        print("\nTrying to use the same backup code again...")
        is_valid_again = mfa.verify_backup_code(user_id, test_backup)
        print(f"Second use: {'✓ Valid' if is_valid_again else '✗ Invalid (expected - single use)'}")
    
    # Step 7: Demonstrate rate limiting
    print("\n🔐 Step 6: Rate Limiting Demo")
    print("-" * 60)
    print("\nMaking 3 failed attempts to trigger rate limiting...")
    
    for i in range(3):
        result = mfa.verify_totp(secret.secret, "000000", user_id)
        print(f"  Attempt {i+1}: {'✓ Valid' if result else '✗ Invalid'}")
        time.sleep(0.5)
    
    # Check if locked out
    if mfa._is_locked_out(user_id):
        print("\n🔒 User is now locked out (15-minute timeout)")
        print("This prevents brute force attacks")
        
        # Even valid codes will fail
        valid_code = mfa.generate_totp(secret.secret)
        result = mfa.verify_totp(secret.secret, valid_code, user_id)
        print(f"\nTrying valid code during lockout: {'✓ Valid' if result else '✗ Blocked (expected)'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("MFA Setup Complete!")
    print("=" * 60)
    print(f"\n✓ MFA enabled: {mfa.is_mfa_enabled(user_id)}")
    print(f"✓ Backup codes: {mfa.get_remaining_backup_codes(user_id)} remaining")
    print(f"✓ Security: Rate limiting active")
    
    print("\n📝 Next Steps:")
    print("  1. Use the secret in your authenticator app")
    print("  2. Store backup codes securely")
    print("  3. Test authentication before deploying")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
