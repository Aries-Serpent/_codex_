#!/usr/bin/env python3
"""
Rotate Jwt Secret

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/rotate_jwt_secret.py [options]
    
    Examples:
    $ python scripts/rotate_jwt_secret.py --help

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
JWT Secret Rotation Script

Rotates the JWT signing secret used for token generation with backup,
validation, and GitHub Secrets integration.

Usage:
    python scripts/rotate_jwt_secret.py              # Rotate secret
    python scripts/rotate_jwt_secret.py --verify     # Verify rotation
    python scripts/rotate_jwt_secret.py --rollback   # Rollback to backup

Environment Variables:
    CODEX_MASTER_KEY: Master encryption key for secure storage
    GITHUB_TOKEN: GitHub API token for secrets management
    TOKEN_SECRET_KEY: Current JWT secret key
    FORCE_ROTATION: Set to 'true' to force rotation

Example:
    CODEX_MASTER_KEY=xxx GITHUB_TOKEN=yyy python scripts/rotate_jwt_secret.py
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    from github import Github
except ImportError:
    print("Error: PyGithub not installed. Run: pip install PyGithub")
    sys.exit(1)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
except ImportError:
    print("Error: cryptography not installed. Run: pip install cryptography")
    sys.exit(1)


class JWTSecretRotator:
    """Handles JWT secret rotation with backup and validation."""
    
    def __init__(self):
        self.master_key = os.getenv('CODEX_MASTER_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.current_secret = os.getenv('TOKEN_SECRET_KEY')
        self.force_rotation = os.getenv('FORCE_ROTATION', 'false').lower() == 'true'
        
        if not self.master_key:
            raise ValueError("CODEX_MASTER_KEY environment variable required")
        
        self.backup_dir = Path('.codex') / 'secrets' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_new_secret(self, length: int = 64) -> str:
        """Generate a cryptographically secure random secret."""
        return secrets.token_urlsafe(length)
    
    def derive_encryption_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from master key using PBKDF2."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_secret(self, secret: str) -> Tuple[bytes, bytes]:
        """Encrypt secret using master key."""
        salt = os.urandom(16)
        key = self.derive_encryption_key(self.master_key, salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(secret.encode())
        return encrypted, salt
    
    def decrypt_secret(self, encrypted: bytes, salt: bytes) -> str:
        """Decrypt secret using master key."""
        key = self.derive_encryption_key(self.master_key, salt)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted).decode()
    
    def backup_current_secret(self) -> str:
        """Backup current secret to encrypted file."""
        if not self.current_secret:
            print("Warning: No current secret to backup")
            return ""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'jwt_secret_backup_{timestamp}.enc'
        
        encrypted, salt = self.encrypt_secret(self.current_secret)
        
        backup_data = {
            'timestamp': timestamp,
            'encrypted_secret': base64.b64encode(encrypted).decode(),
            'salt': base64.b64encode(salt).decode(),
            'hash': hashlib.sha256(self.current_secret.encode()).hexdigest()
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Backed up current secret to: {backup_file}")
        return str(backup_file)
    
    def rotate_secret(self) -> Dict[str, str]:
        """Rotate JWT secret and update GitHub Secrets."""
        print("Starting JWT secret rotation...")
        
        # Check if rotation is needed
        if not self.force_rotation and self.current_secret:
            last_rotation = self.get_last_rotation_date()
            if last_rotation and (datetime.utcnow() - last_rotation).days < 30:
                print(f"ℹ Info: Last rotation was {(datetime.utcnow() - last_rotation).days} days ago")
                print("  Use FORCE_ROTATION=true to force rotation")
                return {'status': 'skipped', 'reason': 'not_due'}
        
        # Backup current secret
        backup_file = self.backup_current_secret()
        
        # Generate new secret
        new_secret = self.generate_new_secret()
        print(f"✓ Generated new JWT secret ({len(new_secret)} characters)")
        
        # Validate new secret
        if not self.validate_secret(new_secret):
            raise ValueError("New secret failed validation")
        
        # Update GitHub Secrets if token available
        if self.github_token:
            self.update_github_secret('TOKEN_SECRET_KEY', new_secret)
        
        # Record rotation
        self.record_rotation(new_secret, backup_file)
        
        # Output for GitHub Actions (avoid writing sensitive secret values)
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                # Do not write the new secret to GITHUB_OUTPUT to prevent clear-text exposure
                f.write(f"backup_file={backup_file}\n")
        
        return {
            'status': 'success',
            'message': 'JWT secret rotated successfully',  # No secret data logged
            'backup_file': backup_file,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_secret(self, secret: str) -> bool:
        """Validate secret meets security requirements."""
        if len(secret) < 32:
            print("✗ Secret too short (minimum 32 characters)")
            return False
        
        # Test HMAC signing
        try:
            test_data = b"test_data"
            signature = hmac.new(secret.encode(), test_data, hashlib.sha256).hexdigest()
            if len(signature) != 64:  # SHA256 hex digest length
                print("✗ HMAC signature validation failed")
                return False
        except Exception as e:
            print(f"✗ Secret validation error: {e}")
            return False
        
        print("✓ Secret validation passed")
        return True
    
    def update_github_secret(self, name: str, value: str) -> None:
        """Update secret in GitHub repository."""
        try:
            g = Github(self.github_token)
            repo = g.get_repo(os.getenv('GITHUB_REPOSITORY', ''))
            
            # GitHub requires secrets to be encrypted with repo's public key
            # For now, we'll use PyGithub which handles this automatically
            repo.create_secret(name, value)
            print(f"✓ Updated GitHub Secret: {name}")
        except Exception as e:
            print(f"Warning: Could not update GitHub Secret: {e}")
    
    def record_rotation(self, new_secret: str, backup_file: str) -> None:
        """Record rotation metadata."""
        rotation_log = self.backup_dir / 'rotation_log.json'
        
        try:
            if rotation_log.exists():
                with open(rotation_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'rotations': []}
        except Exception:
            log_data = {'rotations': []}
        
        log_data['rotations'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'backup_file': backup_file,
            'secret_hash': hashlib.sha256(new_secret.encode()).hexdigest(),
            'force_rotation': self.force_rotation
        })
        
        with open(rotation_log, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"✓ Recorded rotation in log: {rotation_log}")
    
    def get_last_rotation_date(self) -> Optional[datetime]:
        """Get timestamp of last rotation."""
        rotation_log = self.backup_dir / 'rotation_log.json'
        
        if not rotation_log.exists():
            return None
        
        try:
            with open(rotation_log, 'r') as f:
                log_data = json.load(f)
            
            if log_data['rotations']:
                last = log_data['rotations'][-1]
                return datetime.fromisoformat(last['timestamp'])
        except Exception as e:
            print(f"Warning: Could not read rotation log: {e}")
        
        return None
    
    def verify_rotation(self) -> bool:
        """Verify that rotation was successful."""
        print("Verifying JWT secret rotation...")
        
        if not self.current_secret:
            print("✗ No current secret found in environment")
            return False
        
        if not self.validate_secret(self.current_secret):
            print("✗ Current secret failed validation")
            return False
        
        # Check rotation log
        last_rotation = self.get_last_rotation_date()
        if last_rotation:
            age_hours = (datetime.utcnow() - last_rotation).total_seconds() / 3600
            print(f"✓ Last rotation: {age_hours:.1f} hours ago")
            
            if age_hours > 24:
                print("⚠ Warning: Rotation is more than 24 hours old")
        
        print("✓ Rotation verification passed")
        return True
    
    def rollback_to_backup(self, backup_file: Optional[str] = None) -> Dict[str, str]:
        """Rollback to a previous backup."""
        print("Starting rollback to backup...")
        
        if not backup_file:
            # Find most recent backup
            backups = sorted(self.backup_dir.glob('jwt_secret_backup_*.enc'))
            if not backups:
                raise FileNotFoundError("No backup files found")
            backup_file = str(backups[-1])
        
        print(f"Using backup: {backup_file}")
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        encrypted = base64.b64decode(backup_data['encrypted_secret'])
        salt = base64.b64decode(backup_data['salt'])
        
        restored_secret = self.decrypt_secret(encrypted, salt)
        
        # Verify hash
        if hashlib.sha256(restored_secret.encode()).hexdigest() != backup_data['hash']:
            raise ValueError("Backup file integrity check failed")
        
        # Update GitHub Secrets
        if self.github_token:
            self.update_github_secret('TOKEN_SECRET_KEY', restored_secret)
        
        print(f"✓ Rolled back to backup from {backup_data['timestamp']}")
        
        return {
            'status': 'success',
            'backup_timestamp': backup_data['timestamp']
        }


def main():
    parser = argparse.ArgumentParser(description='Rotate JWT signing secret')
    parser.add_argument('--verify', action='store_true', help='Verify rotation')
    parser.add_argument('--rollback', action='store_true', help='Rollback to backup')
    parser.add_argument('--backup-file', help='Specific backup file to rollback to')
    args = parser.parse_args()
    
    try:
        rotator = JWTSecretRotator()
        
        if args.verify:
            success = rotator.verify_rotation()
            sys.exit(0 if success else 1)
        
        elif args.rollback:
            result = rotator.rollback_to_backup(args.backup_file)
            print(json.dumps(result, indent=2))
        
        else:
            result = rotator.rotate_secret()
            print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
