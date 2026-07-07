#!/usr/bin/env python3
"""
Cross-Platform Filename Validator
Detects and reports Windows-incompatible filenames and patterns.
"""

import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict


class FilenameValidator:
    """Validate filenames for cross-platform compatibility."""
    
    # Windows-illegal characters
    WINDOWS_ILLEGAL = r'[<>:"|?*]'
    
    # Patterns that generate unsafe timestamps
    UNSAFE_STRFTIME = re.compile(r"strftime\(['\"]%[YmdHMS]*:%M:%S")
    UNSAFE_ISOFORMAT = re.compile(r"\.isoformat\(\)")
    
    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.violations = defaultdict(list)
        self.code_issues = defaultdict(list)
    
    def check_filenames(self):
        """Check tracked files for Windows-illegal characters."""
        try:
            result = subprocess.run(
                ['git', 'ls-tree', '-r', 'HEAD', '--name-only'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            for filename in result.stdout.strip().split('\n'):
                if filename and re.search(self.WINDOWS_ILLEGAL, Path(filename).name):
                    self.violations[filename] = "Windows-illegal characters"
        except subprocess.CalledProcessError:
            print("❌ Not a git repository")
            return False
        
        return True
    
    def check_python_code(self):
        """Check Python code for unsafe timestamp patterns."""
        for py_file in self.repo_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        # Check for strftime with colons
                        if 'strftime' in line and ('%H:%M:%S' in line or '%H:%M' in line):
                            if any(x in line for x in ['f"', "f'", 'filename', 'path', 'filepath']):
                                rel_path = py_file.relative_to(self.repo_root)
                                self.code_issues[str(rel_path)].append({
                                    'line': i,
                                    'type': 'UNSAFE_STRFTIME',
                                    'content': line.strip()[:100]
                                })
                        
                        # Check for isoformat in filenames
                        if '.isoformat()' in line:
                            if any(x in line for x in ['f"', "f'", 'filename', 'path', 'filepath']):
                                rel_path = py_file.relative_to(self.repo_root)
                                self.code_issues[str(rel_path)].append({
                                    'line': i,
                                    'type': 'UNSAFE_ISOFORMAT',
                                    'content': line.strip()[:100]
                                })
            except Exception:
                pass
    
    def report(self):
        """Generate validation report."""
        print("\n" + "="*60)
        print("CROSS-PLATFORM FILENAME VALIDATION REPORT")
        print("="*60)
        
        # Filename violations
        if self.violations:
            print(f"\n❌ CRITICAL: {len(self.violations)} filenames with Windows-illegal characters:")
            for filename, reason in sorted(self.violations.items()):
                print(f"  • {filename}")
                print(f"    Reason: {reason}")
        else:
            print("\n✅ No filenames with Windows-illegal characters")
        
        # Code issues
        if self.code_issues:
            print(f"\n⚠️  WARNING: {len(self.code_issues)} files with unsafe timestamp patterns:")
            for filepath, issues in sorted(self.code_issues.items())[:20]:
                print(f"\n  📄 {filepath}")
                for issue in issues[:3]:
                    print(f"     Line {issue['line']}: {issue['type']}")
                    print(f"     → {issue['content'][:80]}")
        else:
            print("\n✅ No unsafe timestamp patterns detected")
        
        # Summary
        total_issues = len(self.violations) + len(self.code_issues)
        print("\n" + "-"*60)
        if total_issues == 0:
            print("✅ VALIDATION PASSED: Repository is cross-platform compatible")
            return 0
        else:
            print(f"❌ VALIDATION FAILED: {total_issues} issues found")
            print("\nFor remediation guidance, see:")
            print("  .codex/audit-phase2-filenames.md")
            return 1
    
    def run(self):
        """Execute all checks."""
        print("🔍 Validating filenames for cross-platform compatibility...")
        
        if not self.check_filenames():
            return 1
        
        print("📝 Scanning Python code for unsafe patterns...")
        self.check_python_code()
        
        return self.report()


def main():
    """Main entry point."""
    validator = FilenameValidator()
    exit_code = validator.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
