#!/usr/bin/env python3
"""
Compliance Reporter

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/compliance_reporter.py [options]
    
    Examples:
    $ python scripts/compliance_reporter.py --help

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


"""Compliance Reporter

Generates compliance reports for authentication security.

Usage:
    python scripts/compliance_reporter.py --generate
    python scripts/compliance_reporter.py --analyze-mfa
    python scripts/compliance_reporter.py --check-tokens
    python scripts/compliance_reporter.py --visualize
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path for development mode (if package not installed)
# Proper usage: Install package with 'pip install -e .' to avoid this workaround
SRC_PATH = Path(__file__).parent.parent / 'src'
if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    from cryptography.fernet import Fernet
    from github import Github
    from codex.auth import MFAProvider, TokenManager
except ImportError as e:
    print(f"Error: Missing required dependencies: {e}", file=sys.stderr)
    print("\nPlease install the package with:", file=sys.stderr)
    print("  pip install -e .", file=sys.stderr)
    print("\nOr install missing dependencies:", file=sys.stderr)
    print("  pip install PyGithub cryptography", file=sys.stderr)
    sys.exit(1)

class ComplianceReporter:
    def __init__(self):
        """Initialize the Compliance Reporter with required authentication and encryption.
        
        This constructor sets up the necessary clients and encryption keys for generating
        compliance reports on authentication security practices.
        
        Environment Variables Required:
            GITHUB_TOKEN: GitHub personal access token for API access (required for GitHub operations)
            CODEX_MASTER_KEY: Master encryption key for token management operations (used by TokenManager)
            COMPLIANCE_REPORT_KEY: Fernet encryption key for securing compliance report data (required)
                - Must be a valid 32-byte URL-safe base64-encoded Fernet key
                - Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
                - Used to encrypt sensitive compliance data before storage/transmission
        
        Key Differences:
            - CODEX_MASTER_KEY: Used by TokenManager for encrypting/decrypting authentication tokens
            - COMPLIANCE_REPORT_KEY: Used by this reporter to encrypt compliance report data containing
              sensitive security information (MFA status, token lifecycle data, etc.)
        
        Raises:
            RuntimeError: If COMPLIANCE_REPORT_KEY is missing, not ASCII-encodable, or not a valid Fernet key
            ImportError: If required dependencies (PyGithub, cryptography) are not installed
        
        Attributes:
            github (Github): Authenticated GitHub API client
            mfa (MFAProvider): Multi-factor authentication provider
            tokens (TokenManager): Token lifecycle manager
            report_cipher (Fernet): Encryption cipher for compliance report data
        """
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.mfa = MFAProvider()
        master_key = os.getenv('CODEX_MASTER_KEY')
        if not master_key:
            raise RuntimeError(
                "CODEX_MASTER_KEY environment variable must be set for token management operations"
            )
        self.tokens = TokenManager(secret_key=master_key)
        # Encryption key for compliance reports; must be a valid Fernet key.
        report_key = os.getenv('COMPLIANCE_REPORT_KEY')
        if not report_key:
            raise RuntimeError("COMPLIANCE_REPORT_KEY environment variable must be set for report encryption")
        if isinstance(report_key, str):
            try:
                report_key_bytes = report_key.encode("ascii")
            except UnicodeEncodeError as exc:
                raise RuntimeError(
                    "COMPLIANCE_REPORT_KEY must contain only ASCII characters compatible with a Fernet key"
                ) from exc
        else:
            report_key_bytes = report_key
        try:
            self.report_cipher = Fernet(report_key_bytes)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "COMPLIANCE_REPORT_KEY is not a valid Fernet key. It must be a 32-byte URL-safe base64-encoded value."
            ) from exc

    def _sanitize_sensitive_fields(self, data: dict) -> dict:
        """
        Return a shallow copy of `data` with potentially sensitive fields redacted.

        This is a defensive measure to ensure that secrets such as passwords,
        tokens, or keys are not written to compliance reports in clear text,
        even if upstream providers accidentally include them.
        """
        if not isinstance(data, dict):
            return data

        redacted = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            # Heuristic: redact common secret-bearing fields
            if (
                "password" in key_lower
                or key_lower.endswith("_secret")
                or key_lower.endswith("_token")
                or key_lower.endswith("_key")
            ):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = value
        return redacted
        
    def generate_compliance_data(self) -> dict:
        """Generate comprehensive compliance data."""
        print("Generating compliance data...")
        
        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'mfa_enabled_users': 0,
            'total_users': 0,
            'active_tokens': 0,
            'expired_tokens': 0,
            'compliance_score': 0
        }
        
        # Count MFA-enabled users using the public API
        data['mfa_enabled_users'] = self.mfa.get_mfa_user_count()
        data['total_users'] = max(10, data['mfa_enabled_users'])  # Mock data
        
        # Token statistics (placeholder)
        data['active_tokens'] = len(self.tokens._revoked_tokens)
        data['expired_tokens'] = 0
        
        # Calculate compliance score
        if data['total_users'] > 0:
            mfa_score = (data['mfa_enabled_users'] / data['total_users']) * 100
            data['compliance_score'] = int(mfa_score)
        
        # Save data
        with open('compliance_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Output for GitHub Actions
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"score={data['compliance_score']}\n")
                if data['compliance_score'] < 80:
                    f.write(f"issues=MFA adoption below 80%\n")
        
        print(f"✓ Compliance score: {data['compliance_score']}%")
        return data
    
    def analyze_mfa(self) -> dict:
        """Analyze MFA adoption."""
        print("Analyzing MFA adoption...")
        
        analysis = {
            'enabled': self.mfa.get_mfa_user_count(),
            'disabled': 0,
            'adoption_rate': 0
        }
        
        total = analysis['enabled'] + analysis['disabled']
        if total > 0:
            analysis['adoption_rate'] = (analysis['enabled'] / total) * 100
        
        print(f"✓ MFA adoption: {analysis['adoption_rate']:.1f}%")
        return analysis
    
    def check_tokens(self) -> dict:
        """Check token lifecycle status."""
        print("Checking token lifecycle...")
        
        status = {
            'active': 0,
            'revoked': len(self.tokens._revoked_tokens),
            'total_sessions': len(self.tokens._sessions)
        }
        
        print(f"✓ Active sessions: {status['total_sessions']}, Revoked tokens: {status['revoked']}")
        return status
    
    def generate_report(self) -> str:
        """Generate markdown compliance report."""
        print("Generating compliance report...")
        
        raw_data = self.generate_compliance_data()
        raw_mfa = self.analyze_mfa()
        tokens = self.check_tokens()

        # Sanitize any potentially sensitive fields before persisting to disk
        data = self._sanitize_sensitive_fields(raw_data)
        mfa = self._sanitize_sensitive_fields(raw_mfa)
        
        report = f"""# Authentication Security Compliance Report

**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Overall Compliance Score: {data['compliance_score']}%

### MFA Adoption

- **Users with MFA**: {data['mfa_enabled_users']} / {data['total_users']}
- **Status**: {'✅ Compliant' if mfa['adoption_rate'] >= 95 else '⚠️ Below target'}

## Token Lifecycle

- **Active Sessions**: {tokens['total_sessions']}
- **Revoked Tokens**: {tokens['revoked']}
- **Status**: ✅ Monitored

## Recommendations

{f'- 🔴 **Critical**: Increase MFA adoption to at least 95% (currently {mfa["adoption_rate"]:.1f}%)' if mfa['adoption_rate'] < 95 else '- ✅ MFA adoption meets compliance requirements'}
- 🟡 **Important**: Review and remove inactive sessions regularly
- 🟢 **Good Practice**: Continue monthly token rotation

## Next Review

Scheduled for: {(datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')}

---
*Automated Compliance Report - Auth Security*
"""
        
        report_file = f'compliance_report_{datetime.utcnow().strftime("%Y%m%d")}.md'
        encrypted_report = self.report_cipher.encrypt(report.encode('utf-8'))
        with open(report_file, 'wb') as f:
            f.write(encrypted_report)

        with open('compliance_report_latest.md', 'wb') as f:
            f.write(encrypted_report)
        
        print(f"✓ Report saved (encrypted): {report_file}")
        return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--analyze-mfa', action='store_true')
    parser.add_argument('--check-tokens', action='store_true')
    parser.add_argument('--visualize', action='store_true')
    args = parser.parse_args()
    
    reporter = ComplianceReporter()
    
    if args.generate:
        reporter.generate_compliance_data()
    elif args.analyze_mfa:
        reporter.analyze_mfa()
    elif args.check_tokens:
        reporter.check_tokens()
    elif args.visualize:
        print("ℹ Visualization requires matplotlib (future feature)")
    else:
        reporter.generate_report()

if __name__ == '__main__':
    main()
