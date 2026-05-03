#!/usr/bin/env python3
"""
⚠️ ⚠️ ⚠️  SECURITY WARNING  ⚠️ ⚠️ ⚠️

This file has been DEPRECATED and moved to misc/manual_tools/ for security reasons.

**CRITICAL SECURITY ISSUES:**
- Decodes and potentially logs raw GitHub tokens
- Exposes credentials in memory and logs
- Violates security best practices
- HIGH RISK of token compromise

**DO NOT USE THIS FILE IN AUTOMATED SCRIPTS OR CI/CD PIPELINES**

This tool is preserved ONLY for manual, one-time token extraction in controlled
environments by authorized personnel.

**INSTEAD, USE:**
- scripts/security/verify_token_scope.py - Safe token scope verification
- Environment variables (GITHUB_TOKEN) - Direct token usage
- GitHub API with headers - No decoding needed

**MOVED:** 2026-01-09 (PS-05: Token Security Neutralization)
**REASON:** Critical security vulnerability - token exposure risk

---

🔓 Copilot Token Decoder Module for _codex_ (DEPRECATED)

> Generated: 2025-12-29 | Author: mbaetiong
> Purpose: Decrypt tokens from GitHub secrets for Copilot Agent usage
> **STATUS:** ⛔ DEPRECATED - DO NOT USE

⚡ Energy: 5/5
🧠 Roles: [Copilot Agent], [Security Handler]

DEPRECATED USAGE (DO NOT USE):
    from scripts.security.copilot_token_decoder import copilot_get_github_token

    token = copilot_get_github_token()
    # Use token for GitHub API operations
"""
import base64
import json
import logging
import os
from typing import Optional

# Try to import cryptography, but don't fail if not available
try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class CodexTokenDecoder:
    """Handles secure token decryption for Copilot Agent in _codex_ repository"""

    # Repository-specific authentication data
    REPO_AUTH_DATA = b"_codex_ghp_token_v1_aries_serpent"

    # Priority order for token retrieval methods
    RETRIEVAL_METHODS = [
        'aes_config',      # Most secure: AES-256-GCM combined config
        'aes_separated',   # Secure: AES-256-GCM individual secrets
        'base64',          # Simple: Base64 encoding
        'hex',             # Simple: Hex encoding
        'plaintext'        # Fallback: Plain GITHUB_TOKEN or GH_TOKEN
    ]

    @staticmethod
    def detect_encoding_type() -> str:
        """Auto-detect which encoding method is available in environment"""
        if os.getenv('CODEX_GHP_TOKEN_CONFIG'):
            return 'aes_config'
        if os.getenv('CODEX_GHP_TOKEN_AES_CIPHERTEXT') and os.getenv('CODEX_GHP_TOKEN_AES_KEY'):
            return 'aes_separated'
        if os.getenv('CODEX_GHP_TOKEN_BASE64'):
            return 'base64'
        if os.getenv('CODEX_GHP_TOKEN_HEX'):
            return 'hex'
        if os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN'):
            return 'plaintext'
        return 'none'

    @staticmethod
    def decode_base64() -> Optional[str]:
        """Decode BASE64 encoded token"""
        try:
            encoded_token = os.getenv('CODEX_GHP_TOKEN_BASE64')
            if encoded_token:
                decoded = base64.b64decode(encoded_token).decode('utf-8')
                logger.debug("Token retrieved via Base64 decoding")
                return decoded
        except Exception as e:
            logger.warning(f"Base64 decoding failed: {e}")
        return None

    @staticmethod
    def decode_hex() -> Optional[str]:
        """Decode HEX encoded token"""
        try:
            hex_token = os.getenv('CODEX_GHP_TOKEN_HEX')
            if hex_token:
                decoded = bytes.fromhex(hex_token).decode('utf-8')
                logger.debug("Token retrieved via Hex decoding")
                return decoded
        except Exception as e:
            logger.warning(f"Hex decoding failed: {e}")
        return None

    @staticmethod
    def decrypt_aes_gcm() -> Optional[str]:
        """Decrypt AES-GCM encrypted token"""
        if not CRYPTO_AVAILABLE:
            logger.warning("AES decryption unavailable: cryptography library not installed")
            return None

        try:
            # Try combined config first
            config_b64 = os.getenv('CODEX_GHP_TOKEN_CONFIG')

            if config_b64:
                # Decode combined config
                config = json.loads(base64.b64decode(config_b64).decode())

                # Validate config structure
                if 'aes_config' not in config:
                    logger.error("Invalid AES config: missing aes_config key")
                    return None

                aes_config = config['aes_config']

                key = base64.b64decode(aes_config['key'])
                nonce = base64.b64decode(aes_config['nonce'])
                auth_tag = base64.b64decode(aes_config['auth_tag'])
                ciphertext = base64.b64decode(aes_config['ciphertext'])

                # Use stored auth_data or fall back to default
                auth_data_b64 = aes_config.get('auth_data')
                if auth_data_b64:
                    auth_data = base64.b64decode(auth_data_b64)
                else:
                    auth_data = CodexTokenDecoder.REPO_AUTH_DATA
            else:
                # Try individual secrets
                key_b64 = os.getenv('CODEX_GHP_TOKEN_AES_KEY')
                nonce_b64 = os.getenv('CODEX_GHP_TOKEN_AES_NONCE')
                tag_b64 = os.getenv('CODEX_GHP_TOKEN_AES_TAG')
                ciphertext_b64 = os.getenv('CODEX_GHP_TOKEN_AES_CIPHERTEXT')
                auth_data_b64 = os.getenv('CODEX_GHP_TOKEN_AES_AUTH_DATA')

                if not all([key_b64, nonce_b64, tag_b64, ciphertext_b64]):
                    logger.debug("AES individual secrets not fully configured")
                    return None

                key = base64.b64decode(key_b64)
                nonce = base64.b64decode(nonce_b64)
                auth_tag = base64.b64decode(tag_b64)
                ciphertext = base64.b64decode(ciphertext_b64)

                # Use stored auth_data or fall back to default
                if auth_data_b64:
                    auth_data = base64.b64decode(auth_data_b64)
                else:
                    auth_data = CodexTokenDecoder.REPO_AUTH_DATA

            # Decrypt using AES-GCM
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, auth_tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decryptor.authenticate_additional_data(auth_data)

            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            logger.debug("Token retrieved via AES-256-GCM decryption")
            return plaintext.decode('utf-8')

        except Exception as e:
            logger.warning(f"AES-GCM decryption failed: {e}")

        return None

    @classmethod
    def get_token(cls, method: Optional[str] = None) -> Optional[str]:
        """
        Main method to retrieve decrypted token using best available method

        Args:
            method: Specific retrieval method to use, or None for auto-detect

        Returns:
            Decrypted GitHub token or None if not available
        """
        if method:
            # Use specific method
            retrieval_map = {
                'aes_config': cls.decrypt_aes_gcm,
                'aes_separated': cls.decrypt_aes_gcm,
                'base64': cls.decode_base64,
                'hex': cls.decode_hex,
                'plaintext': lambda: os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
            }

            retrieval_func = retrieval_map.get(method)
            if retrieval_func:
                token = retrieval_func()
                if token:
                    return token

            logger.warning(f"Specified method '{method}' failed or unavailable")
            return None

        # Auto-detect and try methods in priority order
        encoding_type = cls.detect_encoding_type()
        logger.debug(f"Detected encoding type: {encoding_type}")

        if encoding_type == 'aes_config' or encoding_type == 'aes_separated':
            token = cls.decrypt_aes_gcm()
            if token:
                return token

        if encoding_type == 'base64':
            token = cls.decode_base64()
            if token:
                return token

        if encoding_type == 'hex':
            token = cls.decode_hex()
            if token:
                return token

        # Fallback to plaintext environment variables
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        if token:
            logger.debug("Token retrieved from plaintext environment variable")
            return token

        logger.error("No GitHub token found in any configured secret")
        return None

    @classmethod
    def verify_token(cls, token: str) -> bool:
        """
        Verify token format and optionally check against SHA-256 hash

        Args:
            token: Token to verify

        Returns:
            True if token appears valid, False otherwise
        """
        import hashlib

        # Check basic format
        if not token or not token.startswith(('ghp_', 'gho_', 'ghs_', 'github_pat_')):
            logger.warning("Token format validation failed")
            return False

        # Optionally verify against stored SHA-256 hash
        stored_hash = os.getenv('CODEX_GHP_TOKEN_SHA256')
        if stored_hash:
            computed_hash = hashlib.sha256(token.encode()).hexdigest()
            if computed_hash != stored_hash:
                logger.error("Token SHA-256 hash mismatch!")
                return False
            logger.debug("Token SHA-256 hash verified")

        return True


# Convenience function for Copilot Agent
def copilot_get_github_token() -> str:
    """
    Copilot Agent function to retrieve GitHub token

    Returns:
        Decrypted GitHub token

    Raises:
        ValueError: If no token is available in environment secrets
    """
    decoder = CodexTokenDecoder()
    token = decoder.get_token()

    if not token:
        raise ValueError(
            "No GitHub token found in environment secrets. "
            "Please configure CODEX_GHP_TOKEN_* secrets in repository settings."
        )

    # Verify token format
    if not decoder.verify_token(token):
        raise ValueError("Token verification failed: invalid format or hash mismatch")

    return token


# Alternative function with fallback handling
def copilot_get_github_token_safe() -> Optional[str]:
    """
    Safe version of token retrieval that returns None instead of raising

    Returns:
        Decrypted GitHub token or None if not available
    """
    try:
        return copilot_get_github_token()
    except Exception as e:
        logger.error(f"Failed to retrieve GitHub token: {e}")
        return None


if __name__ == '__main__':
    # Test token retrieval when run directly
    print("🔓 _codex_ Token Decoder Test")
    print("="*60)

    decoder = CodexTokenDecoder()
    encoding_type = decoder.detect_encoding_type()

    print(f"Detected encoding type: {encoding_type}")

    if encoding_type == 'none':
        print("❌ No token secrets configured")
        print("\nPlease run: python scripts/security/token_encryption_tool.py")
    else:
        token = decoder.get_token()

        if token:
            # Mask token for display
            masked = f"{token[:10]}...{token[-4:]}"
            print(f"✅ Token retrieved successfully: {masked}")

            # Verify format
            if decoder.verify_token(token):
                print("✅ Token format and hash verified")
            else:
                print("⚠️  Token format/hash verification failed")
        else:
            print("❌ Failed to retrieve token")

    print("="*60)
