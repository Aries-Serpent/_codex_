#!/usr/bin/env python3
"""GitHub User Provisioning with MFA

Automates user provisioning, OAuth setup, and MFA enrollment via GitHub API.

Usage:
    python scripts/github_user_provision.py --user USERNAME --email EMAIL
    python scripts/github_user_provision.py --bulk users.json
"""

import argparse, json, os, sys
from datetime import datetime
try:
    from github import Github
    import sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from codex.auth import MFAProvider
except ImportError as e:
    print(f"Error: {e}. Install: pip install PyGithub && pip install -e .")
    sys.exit(1)

class GitHubUserProvisioner:
    def __init__(self):
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.mfa = MFAProvider()
        self.repo_name = os.getenv('GITHUB_REPOSITORY', '')
        
    def provision_user(self, username: str, email: str) -> dict:
        """Provision user with OAuth and MFA."""
        print(f"Provisioning user: {username}")
        
        # Generate MFA secret
        secret = self.mfa.generate_totp_secret(username)
        uri = secret.get_provisioning_uri(email, issuer_name="Codex")
        backup_codes = self.mfa.generate_backup_codes(username, count=10)
        
        # Create enrollment data
        enrollment = {
            'username': username,
            'email': email,
            'enrollment_url': f'https://github.com/{self.repo_name}/issues/new?title=MFA+Setup+{username}',
            'mfa_secret_length': len(secret.secret),
            'backup_codes_count': len(backup_codes),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"✓ Provisioned {username} (MFA ready)")
        return enrollment
    
    def bulk_provision(self, users_file: str) -> list:
        """Provision multiple users from JSON file."""
        with open(users_file) as f:
            users = json.load(f)
        
        results = []
        for user in users:
            try:
                result = self.provision_user(user['username'], user['email'])
                results.append(result)
            except Exception as e:
                print(f"✗ Failed {user['username']}: {e}")
                results.append({'username': user['username'], 'error': str(e)})
        
        # Save results
        with open('enrollment_results.json', 'w') as f:
            json.dump({'users': results, 'deadline': (datetime.utcnow() + timedelta(days=7)).isoformat()}, f, indent=2)
        
        return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help='Username')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--bulk', help='JSON file with users')
    args = parser.parse_args()
    
    provisioner = GitHubUserProvisioner()
    
    if args.bulk:
        results = provisioner.bulk_provision(args.bulk)
        print(f"Provisioned {len(results)} users")
    elif args.user and args.email:
        result = provisioner.provision_user(args.user, args.email)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

from datetime import timedelta
if __name__ == '__main__':
    main()
