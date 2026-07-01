#!/usr/bin/env python3
"""
Workflow Token Pattern Validator

Validates that all GitHub Actions workflows follow standardized token usage patterns.
Ensures consistent authentication, proper API scopes, and security best practices across
all 209 workflows in the repository.

Usage:
    python3 enforce_token_patterns.py --check-only
    python3 enforce_token_patterns.py --json-output report.json
    python3 enforce_token_patterns.py --fix
    python3 enforce_token_patterns.py --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class TokenPatternValidator:
    """Validates GitHub Actions workflows for proper token pattern usage."""
    
    # Elevated operations that require CODEX_MASTER_KEY
    ELEVATED_OPERATIONS = {
        r'gh\s+pr\s+edit',
        r'gh\s+pr\s+create',
        r'gh\s+workflow\s+run',
        r'gh\s+workflow\s+dispatch',
        r'gh\s+api.*-X\s+PATCH',
        r'gh\s+api.*-X\s+POST',
        r'gh\s+api.*-X\s+PUT',
        r'/actions/variables',
        r'actions/variables',
    }
    
    # Critical operations requiring CODEX_MASTER_KEY without fallback
    CRITICAL_OPERATIONS = {
        r'WEC.*enforcement',
        r'rate.*limit',
        r'session.*state',
        r'/rate_limit',
        r'enforce.*wec',
    }
    
    # Non-existent secrets to reject
    INVALID_SECRETS = {
        'secrets.GITHUB_TOKEN',  # Doesn't exist, use github.token
    }
    
    def __init__(self, workflow_dir: str = '.github/workflows', verbose: bool = False):
        self.workflow_dir = Path(workflow_dir)
        self.verbose = verbose
        self.violations: List[Dict] = []
        self.workflows_checked = 0
        self.workflows_compliant = 0
    
    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def scan_workflows(self) -> Tuple[bool, int, int]:
        """
        Scan all workflow files in the workflow directory.
        
        Returns:
            Tuple of (is_compliant, total_workflows, compliant_workflows)
        """
        if not self.workflow_dir.exists():
            print(f"Error: Workflow directory not found: {self.workflow_dir}")
            return False, 0, 0
        
        workflow_files = sorted(
            self.workflow_dir.glob('*.yml')
        ) + sorted(
            self.workflow_dir.glob('*.yaml')
        )
        
        # Filter out disabled/template files
        workflow_files = [
            f for f in workflow_files
            if not any(suffix in f.name for suffix in ['.disabled', '.template', '.alt', '.tombstone'])
        ]
        
        self.log(f"Found {len(workflow_files)} active workflow files")
        
        for workflow_file in workflow_files:
            self.workflows_checked += 1
            self.validate_workflow(workflow_file)
        
        is_compliant = len(self.violations) == 0
        if is_compliant:
            self.workflows_compliant = self.workflows_checked
        
        return is_compliant, self.workflows_checked, self.workflows_compliant
    
    def validate_workflow(self, workflow_path: Path):
        """Validate a single workflow file."""
        self.log(f"Validating: {workflow_path.name}")
        
        try:
            content = workflow_path.read_text(encoding='utf-8')
        except Exception as e:
            self.violations.append({
                'workflow': workflow_path.name,
                'path': str(workflow_path),
                'rule': 'File Read Error',
                'severity': 'high',
                'message': f'Failed to read workflow file: {e}',
                'line': 0,
                'current': '',
                'suggested': ''
            })
            return
        
        lines = content.split('\n')
        
        # Rule 1: Check for elevated operations without CODEX_MASTER_KEY
        self._check_rule_1_elevated_operations(workflow_path, content, lines)
        
        # Rule 2: Check for invalid secret references
        self._check_rule_2_invalid_secrets(workflow_path, content, lines)
        
        # Rule 3: Check for critical operations
        self._check_rule_3_critical_operations(workflow_path, content, lines)
        
        # Rule 4: Check github.token usage for elevated ops
        self._check_rule_4_token_sufficiency(workflow_path, content, lines)
    
    def _check_rule_1_elevated_operations(self, workflow_path: Path, content: str, lines: List[str]):
        """
        Rule 1: Elevated operations MUST use CODEX_MASTER_KEY
        
        Elevated operations include: PR edits, workflow dispatch, variable writes, etc.
        """
        has_elevated_op = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.ELEVATED_OPERATIONS
        )
        
        if not has_elevated_op:
            self.log(f"  ✓ Rule 1: No elevated operations detected")
            return
        
        # Found elevated operation, check token
        has_master_key = 'CODEX_MASTER_KEY' in content or 'CODEX_BACKUP_KEY' in content
        
        if not has_master_key:
            for line_num, line in enumerate(lines, 1):
                if re.search(r'GH_TOKEN.*github\.token', line):
                    self.violations.append({
                        'workflow': workflow_path.name,
                        'path': str(workflow_path),
                        'rule': 'Rule 1',
                        'severity': 'high',
                        'message': 'Elevated operation detected but token missing CODEX_MASTER_KEY',
                        'line': line_num,
                        'current': line.strip(),
                        'suggested': 'GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}'
                    })
                    return
    
    def _check_rule_2_invalid_secrets(self, workflow_path: Path, content: str, lines: List[str]):
        """
        Rule 2: No references to non-existent secrets
        
        Example: secrets.GITHUB_TOKEN doesn't exist (use github.token instead)
        """
        for invalid_secret in self.INVALID_SECRETS:
            if invalid_secret in content:
                for line_num, line in enumerate(lines, 1):
                    if invalid_secret in line:
                        suggested = line.replace(invalid_secret, 'github.token')
                        self.violations.append({
                            'workflow': workflow_path.name,
                            'path': str(workflow_path),
                            'rule': 'Rule 2',
                            'severity': 'high',
                            'message': f'References non-existent secret: {invalid_secret}',
                            'line': line_num,
                            'current': line.strip(),
                            'suggested': suggested.strip()
                        })
    
    def _check_rule_3_critical_operations(self, workflow_path: Path, content: str, lines: List[str]):
        """
        Rule 3: Critical operations MUST use CODEX_MASTER_KEY without fallback
        
        Critical: WEC enforcement, rate limits, session management
        """
        has_critical_op = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.CRITICAL_OPERATIONS
        )
        
        if not has_critical_op:
            return
        
        # Found critical operation, check for proper token with NO fallback
        has_master_key_only = False
        for line in lines:
            if 'GH_TOKEN' in line and 'CODEX_MASTER_KEY' in line:
                # Check that it doesn't have github.token fallback
                if 'github.token' not in line:
                    has_master_key_only = True
                    break
        
        if not has_master_key_only:
            for line_num, line in enumerate(lines, 1):
                if 'GH_TOKEN' in line or 'GITHUB_TOKEN' in line:
                    self.violations.append({
                        'workflow': workflow_path.name,
                        'path': str(workflow_path),
                        'rule': 'Rule 3',
                        'severity': 'critical',
                        'message': 'Critical operation missing CODEX_MASTER_KEY (requires no fallback)',
                        'line': line_num,
                        'current': line.strip(),
                        'suggested': 'GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}'
                    })
                    return
    
    def _check_rule_4_token_sufficiency(self, workflow_path: Path, content: str, lines: List[str]):
        """
        Rule 4: github.token-only workflows cannot perform elevated operations
        
        If workflow has only github.token but performs elevated operations, it will fail.
        """
        has_elevated_op = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.ELEVATED_OPERATIONS
        )
        
        if not has_elevated_op:
            return
        
        # Check if using only github.token (no CODEX keys)
        uses_only_github_token = (
            'github.token' in content and
            'CODEX_MASTER_KEY' not in content and
            'CODEX_BACKUP_KEY' not in content
        )
        
        if uses_only_github_token:
            for line_num, line in enumerate(lines, 1):
                if 'GH_TOKEN' in line and 'github.token' in line:
                    self.violations.append({
                        'workflow': workflow_path.name,
                        'path': str(workflow_path),
                        'rule': 'Rule 4',
                        'severity': 'high',
                        'message': 'Elevated operation with insufficient token (github.token only)',
                        'line': line_num,
                        'current': line.strip(),
                        'suggested': 'GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}'
                    })
                    return
    
    def get_report(self) -> Dict:
        """Generate compliance report."""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_workflows': self.workflows_checked,
            'compliant': self.workflows_compliant,
            'non_compliant': self.workflows_checked - self.workflows_compliant,
            'compliance_rate': f"{100 * self.workflows_compliant / max(self.workflows_checked, 1):.1f}%",
            'violations': self.violations
        }
    
    def apply_fixes(self) -> bool:
        """
        Apply automatic fixes to workflows.
        
        Returns:
            True if all fixes succeeded
        """
        if not self.violations:
            print("No violations found. No fixes needed.")
            return True
        
        fixed_files = set()
        
        for violation in self.violations:
            workflow_path = Path(violation['path'])
            
            if workflow_path in fixed_files:
                continue  # Already processed this file
            
            try:
                content = workflow_path.read_text(encoding='utf-8')
                original_content = content
                
                # Replace based on rule
                if violation['rule'] == 'Rule 2':
                    # Fix invalid secrets
                    for invalid_secret in self.INVALID_SECRETS:
                        content = content.replace(invalid_secret, 'github.token')
                
                elif violation['rule'] in ['Rule 1', 'Rule 4']:
                    # Add CODEX_MASTER_KEY to github.token-only patterns
                    pattern = r'GH_TOKEN:\s*\$\{\{\s*github\.token\s*\}\}'
                    suggested = 'GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}'
                    content = re.sub(pattern, suggested, content)
                
                elif violation['rule'] == 'Rule 3':
                    # Remove fallback for critical operations
                    pattern = r'GH_TOKEN:\s*\$\{\{\s*secrets\.CODEX_MASTER_KEY\s*\|\|\s*secrets\.CODEX_BACKUP_KEY\s*\|\|\s*github\.token\s*\}\}'
                    suggested = 'GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}'
                    content = re.sub(pattern, suggested, content)
                
                if content != original_content:
                    workflow_path.write_text(content, encoding='utf-8')
                    fixed_files.add(workflow_path)
                    print(f"✓ Fixed: {violation['workflow']}")
            
            except Exception as e:
                print(f"✗ Failed to fix {violation['workflow']}: {e}")
                return False
        
        print(f"\nFixed {len(fixed_files)} workflow file(s)")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate GitHub Actions workflow token patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check compliance without changes
  python3 enforce_token_patterns.py --check-only
  
  # Generate JSON report
  python3 enforce_token_patterns.py --json-output report.json
  
  # Auto-fix violations
  python3 enforce_token_patterns.py --fix
  
  # Verbose output
  python3 enforce_token_patterns.py --verbose
        """
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Check compliance without making changes'
    )
    
    parser.add_argument(
        '--json-output',
        type=str,
        metavar='FILE',
        help='Write JSON report to specified file'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix violations'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--workflows-dir',
        type=str,
        default='.github/workflows',
        help='Path to workflows directory (default: .github/workflows)'
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = TokenPatternValidator(
        workflow_dir=args.workflows_dir,
        verbose=args.verbose
    )
    
    # Scan workflows
    is_compliant, total, compliant = validator.scan_workflows()
    
    # Generate report
    report = validator.get_report()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Workflow Token Pattern Validation Report")
    print(f"{'='*60}")
    print(f"Timestamp:      {report['timestamp']}")
    print(f"Total Workflows: {report['total_workflows']}")
    print(f"Compliant:      {report['compliant']}")
    print(f"Non-Compliant:  {report['non_compliant']}")
    print(f"Compliance:     {report['compliance_rate']}")
    print(f"{'='*60}\n")
    
    # Print violations if any
    if report['violations']:
        print(f"Violations Found ({len(report['violations'])}):\n")
        for i, violation in enumerate(report['violations'][:10], 1):
            print(f"{i}. {violation['workflow']} (Line {violation['line']})")
            print(f"   Rule: {violation['rule']} [{violation['severity'].upper()}]")
            print(f"   Message: {violation['message']}")
            print(f"   Current:   {violation['current']}")
            print(f"   Suggested: {violation['suggested']}")
            print()
        
        if len(report['violations']) > 10:
            print(f"... and {len(report['violations']) - 10} more violations\n")
    else:
        print("✓ All workflows are compliant!\n")
    
    # Write JSON report if requested
    if args.json_output:
        try:
            with open(args.json_output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✓ Report written to: {args.json_output}\n")
        except Exception as e:
            print(f"✗ Failed to write report: {e}\n")
            return 2
    
    # Apply fixes if requested
    if args.fix:
        if not validator.apply_fixes():
            return 2
        print("\n✓ Re-running validation after fixes...\n")
        validator = TokenPatternValidator(
            workflow_dir=args.workflows_dir,
            verbose=args.verbose
        )
        is_compliant, _, _ = validator.scan_workflows()
    
    # Return appropriate exit code
    if is_compliant:
        print("✓ Validation successful!")
        return 0
    else:
        print("✗ Validation failed - non-compliant workflows found")
        return 1


if __name__ == '__main__':
    sys.exit(main())
