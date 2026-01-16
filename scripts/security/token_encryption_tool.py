#!/usr/bin/env python3
"""
Token Encryption Tool

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/security/token_encryption_tool.py [options]
    
    Examples:
    $ python scripts/security/token_encryption_tool.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""
🔐 GitHub Token Encryption Tool for _codex_

> Generated: 2025-12-29 | Author: mbaetiong
> Purpose: Secure token encoding/encryption for _codex_ repository secrets

⚡ Energy: 5/5
🧠 Roles: [Security Engineer], [DevOps Admin]

USAGE:
    python scripts/security/token_encryption_tool.py [--token TOKEN]

ENVIRONMENT VARIABLES:
    GITHUB_TOKEN or GH_TOKEN - Auto-detected if present
"""
import base64
import hashlib
import secrets
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class TokenSecurityManager:
    """Manages secure token transformations for GitHub secrets"""
    
    def __init__(self, token: str):
        self.token = token
        self.results = {}
    
    def generate_base64(self) -> str:
        """Convert token to Base64 encoding"""
        encoded = base64.b64encode(self.token.encode()).decode()
        self.results['BASE64_ENCODED'] = encoded
        return encoded
    
    def generate_hex(self) -> str:
        """Convert token to hexadecimal encoding"""
        hex_encoded = self.token.encode().hex()
        self.results['HEX_ENCODED'] = hex_encoded
        return hex_encoded
    
    def generate_sha256(self) -> str:
        """Generate SHA-256 hash (one-way, for verification only)"""
        sha_hash = hashlib.sha256(self.token.encode()).hexdigest()
        self.results['SHA256_HASH'] = sha_hash
        return sha_hash
    
    def generate_aes_gcm(self) -> dict:
        """Encrypt token using AES-GCM with 256-bit key"""
        if not CRYPTO_AVAILABLE:
            print("❌ AES encryption requires 'cryptography' library")
            return {}
        
        # Generate cryptographically secure key and nonce
        key = secrets.token_bytes(32)  # 256-bit key
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        # Encrypt the token
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add authentication data (repo-specific)
        auth_data = b"_codex_ghp_token_v1_aries_serpent"
        encryptor.authenticate_additional_data(auth_data)
        
        # Encrypt and finalize
        ciphertext = encryptor.update(self.token.encode()) + encryptor.finalize()
        
        # Store results
        self.results['AES_KEY'] = base64.b64encode(key).decode()
        self.results['AES_NONCE'] = base64.b64encode(nonce).decode()
        self.results['AES_AUTH_TAG'] = base64.b64encode(encryptor.tag).decode()
        self.results['AES_CIPHERTEXT'] = base64.b64encode(ciphertext).decode()
        self.results['AES_AUTH_DATA'] = base64.b64encode(auth_data).decode()
        
        return {
            'key': self.results['AES_KEY'],
            'nonce': self.results['AES_NONCE'],
            'auth_tag': self.results['AES_AUTH_TAG'],
            'ciphertext': self.results['AES_CIPHERTEXT'],
            'auth_data': self.results['AES_AUTH_DATA']
        }
    
    def generate_setup_script(self) -> str:
        """Generate a shell script for easy GitHub secrets setup"""
        script = f"""#!/bin/bash
# Generated setup script for _codex_ token secrets
# Generated: {datetime.now().isoformat()}

echo "🔐 Setting up GitHub Secrets for Aries-Serpent/_codex_"
echo "=================================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Install from https://cli.github.com"
    exit 1
fi

# Verify authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
fi

REPO="Aries-Serpent/_codex_"

# Base64 Encoding (Recommended for simplicity)
echo "Adding CODEX_GHP_TOKEN_BASE64..."
gh secret set CODEX_GHP_TOKEN_BASE64 --body "{self.results.get('BASE64_ENCODED', 'NOT_GENERATED')}" --repo "$REPO"

# Hex Encoding (Alternative)
echo "Adding CODEX_GHP_TOKEN_HEX..."
gh secret set CODEX_GHP_TOKEN_HEX --body "{self.results.get('HEX_ENCODED', 'NOT_GENERATED')}" --repo "$REPO"

# SHA-256 Hash (Verification only)
echo "Adding CODEX_GHP_TOKEN_SHA256..."
gh secret set CODEX_GHP_TOKEN_SHA256 --body "{self.results.get('SHA256_HASH', 'NOT_GENERATED')}" --repo "$REPO"
"""
        
        # Add AES secrets if available
        if self.results.get('AES_KEY'):
            script += f"""
# AES-256-GCM Encryption (Most Secure - Recommended)
echo "Adding CODEX_GHP_TOKEN_AES_KEY..."
gh secret set CODEX_GHP_TOKEN_AES_KEY --body "{self.results['AES_KEY']}" --repo "$REPO"

echo "Adding CODEX_GHP_TOKEN_AES_CIPHERTEXT..."
gh secret set CODEX_GHP_TOKEN_AES_CIPHERTEXT --body "{self.results['AES_CIPHERTEXT']}" --repo "$REPO"

echo "Adding CODEX_GHP_TOKEN_AES_NONCE..."
gh secret set CODEX_GHP_TOKEN_AES_NONCE --body "{self.results['AES_NONCE']}" --repo "$REPO"

echo "Adding CODEX_GHP_TOKEN_AES_TAG..."
gh secret set CODEX_GHP_TOKEN_AES_TAG --body "{self.results['AES_AUTH_TAG']}" --repo "$REPO"

echo "Adding CODEX_GHP_TOKEN_AES_AUTH_DATA..."
gh secret set CODEX_GHP_TOKEN_AES_AUTH_DATA --body "{self.results['AES_AUTH_DATA']}" --repo "$REPO"
"""
            
            # Add combined config
            combined_config = {
                'version': '1.0',
                'repo': 'Aries-Serpent/_codex_',
                'encryption_method': 'AES-256-GCM',
                'aes_config': {
                    'key': self.results['AES_KEY'],
                    'nonce': self.results['AES_NONCE'],
                    'auth_tag': self.results['AES_AUTH_TAG'],
                    'ciphertext': self.results['AES_CIPHERTEXT'],
                    'auth_data': self.results['AES_AUTH_DATA']
                }
            }
            config_b64 = base64.b64encode(json.dumps(combined_config).encode()).decode()
            
            script += f"""
# Combined AES Config (Single Secret Alternative)
echo "Adding CODEX_GHP_TOKEN_CONFIG..."
gh secret set CODEX_GHP_TOKEN_CONFIG --body "{config_b64}" --repo "$REPO"
"""
        
        script += """
echo ""
echo "✅ All secrets have been set successfully!"
echo ""
echo "🔄 NEXT STEPS:"
echo "1. Revoke the original GitHub token"
echo "2. Test Copilot Agent token retrieval"
echo "3. Update any workflows that use GITHUB_TOKEN"
echo ""
echo "=================================================="
"""
        
        return script
    
    def print_results(self):
        """Print all encryption results formatted for GitHub Secrets"""
        print("\n" + "="*80)
        print("🔐 TOKEN ENCRYPTION RESULTS FOR _CODEX_ REPOSITORY")
        print("="*80)
        print(f"⚠️  Original Token: {self.token[:10]}...{self.token[-4:]} (NEVER COMMIT)")
        print("="*80)
        
        print("\n📋 COPY THESE VALUES TO GITHUB SECRETS:")
        print("\n🔗 URL: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions")
        print("\n" + "─"*80)
        
        # Recommended: Base64
        if 'BASE64_ENCODED' in self.results:
            print(f"\n🥇 RECOMMENDED - Base64 Encoding:")
            print(f"   Secret Name:  CODEX_GHP_TOKEN_BASE64")
            print(f"   Secret Value: {self.results['BASE64_ENCODED']}")
        
        # Alternative: Hex
        if 'HEX_ENCODED' in self.results:
            print(f"\n🥈 ALTERNATIVE - Hex Encoding:")
            print(f"   Secret Name:  CODEX_GHP_TOKEN_HEX")
            print(f"   Secret Value: {self.results['HEX_ENCODED']}")
        
        # Verification: SHA-256
        if 'SHA256_HASH' in self.results:
            print(f"\n🔍 VERIFICATION - SHA-256 Hash:")
            print(f"   Secret Name:  CODEX_GHP_TOKEN_SHA256")
            print(f"   Secret Value: {self.results['SHA256_HASH']}")
        
        # Most Secure: AES-256-GCM
        if 'AES_KEY' in self.results:
            print(f"\n🔐 MOST SECURE - AES-256-GCM Encryption:")
            print(f"   Secret Name:  CODEX_GHP_TOKEN_AES_KEY")
            print(f"   Secret Value: {self.results['AES_KEY']}")
            print(f"\n   Secret Name:  CODEX_GHP_TOKEN_AES_CIPHERTEXT")
            print(f"   Secret Value: {self.results['AES_CIPHERTEXT']}")
            print(f"\n   Secret Name:  CODEX_GHP_TOKEN_AES_NONCE")
            print(f"   Secret Value: {self.results['AES_NONCE']}")
            print(f"\n   Secret Name:  CODEX_GHP_TOKEN_AES_TAG")
            print(f"   Secret Value: {self.results['AES_AUTH_TAG']}")
            print(f"\n   Secret Name:  CODEX_GHP_TOKEN_AES_AUTH_DATA")
            print(f"   Secret Value: {self.results['AES_AUTH_DATA']}")
            
            # Combined config option
            combined_config = {
                'version': '1.0',
                'repo': 'Aries-Serpent/_codex_',
                'encryption_method': 'AES-256-GCM',
                'aes_config': {
                    'key': self.results['AES_KEY'],
                    'nonce': self.results['AES_NONCE'],
                    'auth_tag': self.results['AES_AUTH_TAG'],
                    'ciphertext': self.results['AES_CIPHERTEXT'],
                    'auth_data': self.results['AES_AUTH_DATA']
                }
            }
            config_b64 = base64.b64encode(json.dumps(combined_config).encode()).decode()
            
            print(f"\n📦 COMBINED AES CONFIG (Single Secret Option):")
            print(f"   Secret Name:  CODEX_GHP_TOKEN_CONFIG")
            print(f"   Secret Value: {config_b64}")
        
        print("\n" + "="*80)
    
    def save_setup_script(self, output_path: str = None):
        """Save the setup script to a file"""
        if not output_path:
            output_path = Path.home() / 'codex_token_setup.sh'
        
        script_content = self.generate_setup_script()
        output_file = Path(output_path)
        
        output_file.write_text(script_content)
        os.chmod(output_file, 0o700)  # Make executable, owner-only
        
        print(f"\n💾 Setup script saved to: {output_file}")
        print(f"   Run with: bash {output_file}")
        print(f"   Or review and copy commands manually")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='_codex_ GitHub Token Encryption Tool',
        epilog='Security Level: 5/5 🔐'
    )
    parser.add_argument(
        '--token',
        help='GitHub token to encrypt (or set GITHUB_TOKEN env var)'
    )
    parser.add_argument(
        '--output-script',
        help='Save setup script to file (default: ~/codex_token_setup.sh)'
    )
    parser.add_argument(
        '--no-aes',
        action='store_true',
        help='Skip AES encryption (use only Base64/Hex)'
    )
    
    args = parser.parse_args()
    
    print("\n🔐 _CODEX_ TOKEN ENCRYPTION TOOL v2.0")
    print("⚡ Energy: 5/5 | 🧠 Security Mode Active")
    print("🎯 Repository: Aries-Serpent/_codex_")
    print("="*80)
    
    # Get token from args or environment
    token = args.token
    if not token:
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    
    if not token:
        token = input("\nEnter GitHub token (or Ctrl+C to cancel): ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
    
    # Validate token format
    if not token.startswith(('ghp_', 'gho_', 'ghs_', 'github_pat_')):
        print("⚠️  Warning: Token doesn't match expected GitHub format")
        confirm = input("   Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            sys.exit(1)
    
    # Initialize manager and generate all formats
    manager = TokenSecurityManager(token)
    
    # Generate encodings
    manager.generate_base64()
    manager.generate_hex()
    manager.generate_sha256()
    
    # Generate AES encryption if available and not disabled
    if CRYPTO_AVAILABLE and not args.no_aes:
        manager.generate_aes_gcm()
    elif not CRYPTO_AVAILABLE:
        print("\n⚠️  AES encryption skipped (cryptography library not installed)")
        print("   Install with: pip install cryptography")
    
    # Print results
    manager.print_results()
    
    # Save setup script
    manager.save_setup_script(args.output_script)
    
    print("\n✅ Encryption complete!")
    print("\n🔄 NEXT STEPS:")
    print("1. Run the generated setup script (recommended):")
    print("   bash ~/codex_token_setup.sh")
    print("\n2. OR manually add secrets via GitHub UI:")
    print("   https://github.com/Aries-Serpent/_codex_/settings/secrets/actions")
    print("\n3. Revoke the original token after verifying setup")
    print("\n4. Test Copilot Agent token retrieval")
    print("="*80)


if __name__ == "__main__":
    main()
