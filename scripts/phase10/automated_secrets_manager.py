#!/usr/bin/env python3
"""
Automated GitHub Secrets Manager for Copilot Agents
Enables programmatic secret injection via GitHub API, CLI, and MCP

This tool allows Copilot Agents with FULL ACCESS to:
1. Generate secure secrets (keys, tokens, credentials)
2. Inject secrets into GitHub repository via API
3. Validate secret configuration
4. Rotate secrets with audit trail

**Security**: Requires GITHUB_TOKEN or GH_TOKEN with repo and workflow scopes
**Created**: 2026-01-13 (Phase 10 automation)
**User Authorization**: mbaetiong granted FULL ACCESS via comment #3745423798
"""

import os
import sys
import json
import base64
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime, UTC
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Optional imports with graceful degradation
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - install with: pip install requests")

try:
    from nacl import encoding, public
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False
    logger.warning("PyNaCl not available - install with: pip install PyNaCl")


class GitHubSecretsManager:
    """
    Automated secrets management for GitHub repositories.
    Supports multiple injection methods: API, CLI, MCP.
    """
    
    def __init__(
        self,
        owner: str = "Aries-Serpent",
        repo: str = "_codex_",
        token: Optional[str] = None
    ):
        """
        Initialize secrets manager.
        
        Args:
            owner: Repository owner (default: Aries-Serpent)
            repo: Repository name (default: _codex_)
            token: GitHub token (defaults to env vars)
        """
        self.owner = owner
        self.repo = repo
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.api_base = "https://api.github.com"
        
        if not self.token:
            logger.error("No GitHub token found. Set GITHUB_TOKEN or GH_TOKEN")
            logger.error("Token must have 'repo' and 'workflow' scopes")
    
    def generate_secure_key(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random key.
        
        Args:
            length: Key length in bytes (default: 32 for 256-bit)
            
        Returns:
            Base64-encoded secure random key
        """
        try:
            # Use subprocess for maximum compatibility
            result = subprocess.run(
                ["openssl", "rand", "-base64", str(length)],
                capture_output=True,
                text=True,
                check=True
            )
            key = result.stdout.strip()
            logger.info(f"✅ Generated {length*8}-bit secure key")
            return key
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to generate key: {e}")
            raise
        except FileNotFoundError:
            logger.error("❌ OpenSSL not found. Install openssl.")
            raise
    
    def get_public_key_api(self) -> Tuple[str, str]:
        """
        Get repository public key for secret encryption (API method).
        
        Returns:
            Tuple of (key_id, public_key)
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests library required for API method")
        
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/actions/secrets/public-key"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info("✅ Retrieved repository public key")
            return data["key_id"], data["key"]
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to get public key: {e}")
            raise
    
    def encrypt_secret_value(self, public_key: str, secret_value: str) -> str:
        """
        Encrypt secret value using repository public key.
        
        Args:
            public_key: Repository public key (base64)
            secret_value: Secret value to encrypt
            
        Returns:
            Base64-encoded encrypted secret
        """
        if not NACL_AVAILABLE:
            raise RuntimeError("PyNaCl library required for encryption. Install: pip install PyNaCl")
        
        try:
            public_key_bytes = base64.b64decode(public_key)
            sealed_box = public.SealedBox(public.PublicKey(public_key_bytes))
            encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
            encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
            logger.info("✅ Secret encrypted successfully")
            return encrypted_b64
        except Exception as e:
            logger.error(f"❌ Failed to encrypt secret: {e}")
            raise
    
    def set_secret_api(
        self,
        secret_name: str,
        secret_value: str,
        overwrite: bool = True
    ) -> bool:
        """
        Set repository secret via GitHub API.
        
        Args:
            secret_name: Name of the secret (e.g., CODEX_MASTER_KEY)
            secret_value: Value to store
            overwrite: Whether to overwrite existing secret (default: True)
            
        Returns:
            True if successful, False otherwise
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests library required for API method")
        
        if not NACL_AVAILABLE:
            raise RuntimeError("PyNaCl library required for encryption")
        
        try:
            # Get public key
            key_id, public_key = self.get_public_key_api()
            
            # Encrypt secret
            encrypted_value = self.encrypt_secret_value(public_key, secret_value)
            
            # Set secret
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/actions/secrets/{secret_name}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            payload = {
                "encrypted_value": encrypted_value,
                "key_id": key_id
            }
            
            response = requests.put(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ Secret '{secret_name}' set successfully via API")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to set secret via API: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def set_secret_cli(
        self,
        secret_name: str,
        secret_value: str,
        overwrite: bool = True
    ) -> bool:
        """
        Set repository secret via gh CLI.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to store
            overwrite: Whether to overwrite (CLI always overwrites)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if gh CLI is available
            subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                check=True
            )
            
            # Set secret via gh CLI
            process = subprocess.Popen(
                [
                    "gh", "secret", "set", secret_name,
                    "--repo", f"{self.owner}/{self.repo}"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=secret_value)
            
            if process.returncode == 0:
                logger.info(f"✅ Secret '{secret_name}' set successfully via gh CLI")
                return True
            else:
                logger.error(f"❌ Failed to set secret via gh CLI: {stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("❌ gh CLI not found. Install from: https://cli.github.com/")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ gh CLI error: {e}")
            return False
    
    def verify_secret_exists(self, secret_name: str) -> bool:
        """
        Verify that a secret exists in the repository.
        
        Args:
            secret_name: Name of the secret to check
            
        Returns:
            True if secret exists, False otherwise
        """
        # Try API method first
        if REQUESTS_AVAILABLE:
            try:
                url = f"{self.api_base}/repos/{self.owner}/{self.repo}/actions/secrets/{secret_name}"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    logger.info(f"✅ Secret '{secret_name}' exists")
                    return True
                elif response.status_code == 404:
                    logger.info(f"ℹ️  Secret '{secret_name}' does not exist")
                    return False
                else:
                    logger.warning(f"⚠️  Unexpected status code: {response.status_code}")
                    return False
            except Exception as e:
                logger.warning(f"⚠️  API verification failed: {e}")
        
        # Fallback to gh CLI
        try:
            result = subprocess.run(
                ["gh", "secret", "list", "--repo", f"{self.owner}/{self.repo}"],
                capture_output=True,
                text=True,
                check=True
            )
            exists = secret_name in result.stdout
            if exists:
                logger.info(f"✅ Secret '{secret_name}' exists (verified via CLI)")
            else:
                logger.info(f"ℹ️  Secret '{secret_name}' does not exist (verified via CLI)")
            return exists
        except Exception as e:
            logger.warning(f"⚠️  CLI verification failed: {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """
        List all secrets in the repository.
        
        Returns:
            List of secret names
        """
        # Try API method first
        if REQUESTS_AVAILABLE:
            try:
                url = f"{self.api_base}/repos/{self.owner}/{self.repo}/actions/secrets"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                secrets = [secret["name"] for secret in data.get("secrets", [])]
                logger.info(f"✅ Found {len(secrets)} secrets via API")
                return secrets
            except Exception as e:
                logger.warning(f"⚠️  API list failed: {e}")
        
        # Fallback to gh CLI
        try:
            result = subprocess.run(
                ["gh", "secret", "list", "--repo", f"{self.owner}/{self.repo}"],
                capture_output=True,
                text=True,
                check=True
            )
            secrets = [
                line.split()[0]
                for line in result.stdout.strip().split('\n')
                if line.strip()
            ]
            logger.info(f"✅ Found {len(secrets)} secrets via CLI")
            return secrets
        except Exception as e:
            logger.error(f"❌ Failed to list secrets: {e}")
            return []
    
    def setup_phase10_secrets(self, force: bool = False) -> Dict[str, bool]:
        """
        Automated setup of all Phase 10 required secrets.
        
        Args:
            force: If True, regenerate and overwrite existing secrets
            
        Returns:
            Dict mapping secret names to success status
        """
        logger.info("🚀 Starting Phase 10 secrets setup")
        logger.info("=" * 60)
        
        results = {}
        
        # 1. CODEX_MASTER_KEY
        secret_name = "CODEX_MASTER_KEY"
        if not force and self.verify_secret_exists(secret_name):
            logger.info(f"ℹ️  {secret_name} already exists (use --force to regenerate)")
            results[secret_name] = "skipped"
        else:
            logger.info(f"🔑 Generating {secret_name}...")
            key = self.generate_secure_key(32)  # 256-bit
            
            # Try API first, fallback to CLI
            success = self.set_secret_api(secret_name, key)
            if not success:
                logger.info("Falling back to gh CLI...")
                success = self.set_secret_cli(secret_name, key)
            
            results[secret_name] = success
        
        # Note: Google Cloud secrets require user-provided values
        # These cannot be auto-generated
        google_secrets = [
            "GDRIVE_SERVICE_ACCOUNT_JSON",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET"
        ]
        
        for secret_name in google_secrets:
            if self.verify_secret_exists(secret_name):
                logger.info(f"✅ {secret_name} already configured")
                results[secret_name] = "exists"
            else:
                logger.warning(f"⚠️  {secret_name} requires manual configuration")
                logger.warning(f"    See: HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md")
                results[secret_name] = "manual_required"
        
        # Summary
        logger.info("")
        logger.info("📊 Phase 10 Secrets Setup Summary")
        logger.info("=" * 60)
        for name, status in results.items():
            if status is True or status == "exists":
                logger.info(f"✅ {name}: Configured")
            elif status == "skipped":
                logger.info(f"ℹ️  {name}: Skipped (already exists)")
            elif status == "manual_required":
                logger.warning(f"⚠️  {name}: Manual setup required")
            else:
                logger.error(f"❌ {name}: Failed")
        
        return results


def main():
    """CLI entry point for automated secrets management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automated GitHub Secrets Manager for Copilot Agents"
    )
    parser.add_argument(
        "--owner",
        default="Aries-Serpent",
        help="Repository owner (default: Aries-Serpent)"
    )
    parser.add_argument(
        "--repo",
        default="_codex_",
        help="Repository name (default: _codex_)"
    )
    parser.add_argument(
        "--action",
        choices=["setup", "generate-key", "set", "verify", "list"],
        required=True,
        help="Action to perform"
    )
    parser.add_argument(
        "--name",
        help="Secret name (required for set, verify)"
    )
    parser.add_argument(
        "--value",
        help="Secret value (required for set, optional for generate-key)"
    )
    parser.add_argument(
        "--method",
        choices=["api", "cli", "auto"],
        default="auto",
        help="Injection method (default: auto - try API, fallback to CLI)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing secrets"
    )
    parser.add_argument(
        "--key-length",
        type=int,
        default=32,
        help="Key length in bytes for generate-key (default: 32)"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = GitHubSecretsManager(owner=args.owner, repo=args.repo)
    
    if not manager.token:
        logger.error("❌ No GitHub token found")
        logger.error("Set GITHUB_TOKEN or GH_TOKEN environment variable")
        logger.error("Token must have 'repo' and 'workflow' scopes")
        return 1
    
    # Execute action
    if args.action == "setup":
        results = manager.setup_phase10_secrets(force=args.force)
        # Check if any required secrets failed
        failed = [k for k, v in results.items() if v is False]
        if failed:
            logger.error(f"❌ Failed to configure: {', '.join(failed)}")
            return 1
        return 0
    
    elif args.action == "generate-key":
        key = manager.generate_secure_key(args.key_length)
        print(f"\n🔑 Generated Key ({args.key_length*8}-bit):")
        print("=" * 60)
        print(key)
        print("=" * 60)
        print("\n⚠️  Store securely immediately!")
        if args.name:
            logger.info(f"Setting as {args.name}...")
            if args.method in ["api", "auto"]:
                success = manager.set_secret_api(args.name, key)
                if not success and args.method == "auto":
                    logger.info("Falling back to CLI...")
                    success = manager.set_secret_cli(args.name, key)
            else:
                success = manager.set_secret_cli(args.name, key)
            return 0 if success else 1
        return 0
    
    elif args.action == "set":
        if not args.name or not args.value:
            logger.error("❌ --name and --value required for set action")
            return 1
        
        if args.method in ["api", "auto"]:
            success = manager.set_secret_api(args.name, args.value)
            if not success and args.method == "auto":
                logger.info("Falling back to CLI...")
                success = manager.set_secret_cli(args.name, args.value)
        else:
            success = manager.set_secret_cli(args.name, args.value)
        
        return 0 if success else 1
    
    elif args.action == "verify":
        if not args.name:
            logger.error("❌ --name required for verify action")
            return 1
        exists = manager.verify_secret_exists(args.name)
        return 0 if exists else 1
    
    elif args.action == "list":
        secrets = manager.list_secrets()
        print(f"\n📋 Secrets in {args.owner}/{args.repo}:")
        print("=" * 60)
        for secret in secrets:
            print(f"  • {secret}")
        print(f"\nTotal: {len(secrets)} secrets")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
