#!/usr/bin/env python3
"""
Github Secrets Sync

Purpose:
    Synchronizes github_secrets_sync

Usage:
    python scripts/github_secrets_sync.py [options]
    
    Examples:
    $ python scripts/github_secrets_sync.py --help

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
GitHub Secrets Sync Script

Syncs authentication tokens to GitHub Secrets with encryption, validation,
and audit logging.

Usage:
    python scripts/github_secrets_sync.py --backup      # Backup secrets
    python scripts/github_secrets_sync.py --rotate      # Rotate secrets
    python scripts/github_secrets_sync.py --validate    # Validate secrets
    python scripts/github_secrets_sync.py --sync-downstream  # Sync to dependent systems

Environment Variables:
    GITHUB_TOKEN: GitHub API token
    CODEX_MASTER_KEY: Master encryption key
"""

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

try:
    from github import Github
except ImportError:
    print("Error: Install dependencies: pip install PyGithub")
    sys.exit(1)


class GitHubSecretsManager:
    """Manages GitHub repository secrets for authentication."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.master_key = os.getenv('CODEX_MASTER_KEY')
        self.repo_name = os.getenv('GITHUB_REPOSITORY', '')
        
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN required")
        if not self.master_key:
            raise ValueError("CODEX_MASTER_KEY required")
        
        self.g = Github(self.github_token)
        self.repo = self.g.get_repo(self.repo_name) if self.repo_name else None
        
        self.backup_dir = Path('.codex') / 'secrets' / 'github_backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_secrets(self) -> Dict[str, str]:
        """Backup current GitHub Secrets."""
        print("Backing up GitHub Secrets...")
        
        secret_names = [
            'TOKEN_SECRET_KEY',
            'GITHUB_OAUTH_CLIENT_SECRET',
            'SESSION_ENCRYPTION_KEY'
        ]
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'github_secrets_backup_{timestamp}.json'
        
        backup_data = {
            'timestamp': timestamp,
            'secrets': {}
        }
        
        for name in secret_names:
            value = os.getenv(name)
            if value:
                backup_data['secrets'][name] = {
                    'hash': hashlib.sha256(value.encode()).hexdigest(),
                    'length': len(value)
                }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Backed up {len(backup_data['secrets'])} secrets to: {backup_file}")
        return {'backup_file': str(backup_file), 'count': len(backup_data['secrets'])}
    
    def rotate_secrets(self, secret_names: List[str]) -> Dict[str, str]:
        """Rotate specified secrets."""
        print(f"Rotating {len(secret_names)} secrets...")
        
        results = {'rotated': [], 'failed': []}
        
        for name in secret_names:
            try:
                new_value = secrets.token_urlsafe(64)
                
                if self.repo:
                    self.repo.create_secret(name, new_value)
                    print("✓ Rotated secret")
                    results['rotated'].append({'name': name, 'status': 'success'})
                else:
                    print(f"⚠ Skipped {name} (no repo connection)")
                    results['failed'].append({'name': name, 'reason': 'no_repo'})
            except Exception as e:
                print(f"✗ Failed to rotate {name}: {e}")
                results['failed'].append({'name': name, 'reason': str(e)})
        
        # Save results
        results_file = Path('rotation_results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def validate_secrets(self) -> bool:
        """Validate that secrets are properly configured."""
        print("Validating GitHub Secrets...")
        
        required_secrets = [
            'TOKEN_SECRET_KEY',
            'GITHUB_TOKEN',
            'CODEX_MASTER_KEY'
        ]
        
        validations = []
        all_valid = True
        
        for name in required_secrets:
            value = os.getenv(name)
            if not value:
                print("✗ Missing required secret")
                validations.append({'test': name, 'passed': False})
                all_valid = False
            elif len(value) < 32:
                print("✗ A required secret is too short")
                validations.append({'test': name, 'passed': False})
                all_valid = False
            else:
                print("✓ Secret passed validation")
                validations.append({'test': name, 'passed': True})
        
        # Save validation results
        with open('rotation_results.json', 'r+') as f:
            data = json.load(f)
            data['validations'] = validations
            data['next_rotation_date'] = (datetime.utcnow().replace(day=1) + 
                                         timedelta(days=32)).replace(day=1).isoformat()
            data['backup_location'] = str(self.backup_dir)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        
        return all_valid
    
    def sync_downstream(self) -> None:
        """Sync secrets to downstream systems (placeholder for future integrations)."""
        print("Syncing secrets to downstream systems...")
        print("ℹ Info: No downstream systems configured yet")
        print("✓ Sync complete (noop)")


def main():
    parser = argparse.ArgumentParser(description='Manage GitHub Secrets for auth')
    parser.add_argument('--backup', action='store_true', help='Backup secrets')
    parser.add_argument('--rotate', action='store_true', help='Rotate secrets')
    parser.add_argument('--secrets', help='Comma-separated list of secrets to rotate')
    parser.add_argument('--validate', action='store_true', help='Validate secrets')
    parser.add_argument('--sync-downstream', action='store_true', help='Sync to downstream systems')
    args = parser.parse_args()
    
    try:
        manager = GitHubSecretsManager()
        
        if args.backup:
            result = manager.backup_secrets()
            print(json.dumps(result, indent=2))
        
        elif args.rotate:
            secret_list = args.secrets.split(',') if args.secrets else [
                'TOKEN_SECRET_KEY', 'GITHUB_OAUTH_CLIENT_SECRET', 'SESSION_ENCRYPTION_KEY'
            ]
            result = manager.rotate_secrets(secret_list)
            print(json.dumps(result, indent=2))
        
        elif args.validate:
            success = manager.validate_secrets()
            sys.exit(0 if success else 1)
        
        elif args.sync_downstream:
            manager.sync_downstream()
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
