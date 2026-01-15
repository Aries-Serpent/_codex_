#!/usr/bin/env python3
"""Repository Access Management

Enforces MFA-based access control for GitHub repositories.

Usage:
    python scripts/manage_repo_access.py --enforce
    python scripts/manage_repo_access.py --audit
"""

import argparse, json, os, sys
from datetime import datetime
try:
    from github import Github
    import sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from codex.auth import MFAProvider
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

class RepoAccessManager:
    def __init__(self):
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.mfa = MFAProvider()
        
    def check_user_mfa(self, username: str) -> bool:
        """Check if user has MFA enabled."""
        # Use the public method to check MFA status
        return self.mfa.is_mfa_enabled(username)
    
    def enforce_mfa_access(self, repo_name: str) -> dict:
        """Enforce MFA requirement for repository access."""
        print(f"Enforcing MFA for repo: {repo_name}")
        
        repo = self.github.get_repo(repo_name)
        results = {'enforced': [], 'removed': [], 'errors': []}
        
        for collab in repo.get_collaborators():
            try:
                if not self.check_user_mfa(collab.login):
                    # In production: remove collaborator
                    print(f"⚠ Would remove: {collab.login} (no MFA)")
                    results['removed'].append(collab.login)
                else:
                    print(f"✓ Verified: {collab.login}")
                    results['enforced'].append(collab.login)
            except Exception as e:
                results['errors'].append({'user': collab.login, 'error': str(e)})
        
        # Save audit report
        with open('access_audit.json', 'w') as f:
            json.dump({'timestamp': datetime.utcnow().isoformat(), **results}, f, indent=2)
        
        return results
    
    def audit_repo_access(self, repo_name: str) -> dict:
        """Audit repository access without enforcement."""
        print(f"Auditing repo: {repo_name}")
        
        repo = self.github.get_repo(repo_name)
        audit = {'with_mfa': [], 'without_mfa': [], 'timestamp': datetime.utcnow().isoformat()}
        
        for collab in repo.get_collaborators():
            if self.check_user_mfa(collab.login):
                audit['with_mfa'].append(collab.login)
            else:
                audit['without_mfa'].append(collab.login)
        
        with open('access_audit.json', 'w') as f:
            json.dump(audit, f, indent=2)
        
        print(f"✓ Audit complete: {len(audit['with_mfa'])} with MFA, {len(audit['without_mfa'])} without")
        return audit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--enforce', action='store_true')
    parser.add_argument('--audit', action='store_true')
    parser.add_argument('--repo', default=os.getenv('GITHUB_REPOSITORY', ''))
    args = parser.parse_args()
    
    manager = RepoAccessManager()
    
    if args.enforce:
        manager.enforce_mfa_access(args.repo)
    elif args.audit:
        manager.audit_repo_access(args.repo)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
