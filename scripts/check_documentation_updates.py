#!/usr/bin/env python3
"""
Check Documentation Updates

Purpose:
    Updates check_documentation_updates

Usage:
    python scripts/check_documentation_updates.py [options]
    
    Examples:
    $ python scripts/check_documentation_updates.py --help

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
Systematic Documentation Update Checker

This script ensures all documentation is updated before concluding work.
It checks for:
1. README files that need updating based on code changes
2. AGENTS.md files that reference changed modules
3. Outdated examples in documentation
4. Missing documentation for new features
5. Changelog entries for significant changes

Usage:
    python scripts/check_documentation_updates.py
    python scripts/check_documentation_updates.py --fix
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class DocumentationChecker:
    """Check and update documentation systematically."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.issues = []
        self.fixed = []
        
    def find_all_documentation(self) -> dict[str, list[Path]]:
        """Find all documentation files in the repository."""
        docs = {
            'README': [],
            'AGENTS': [],
            'CHANGELOG': [],
            'docs': [],
        }
        
        for pattern, key in [
            ('**/README.md', 'README'),
            ('**/AGENTS.md', 'AGENTS'),
            ('**/CHANGELOG.md', 'CHANGELOG'),
            ('docs/**/*.md', 'docs'),
        ]:
            for path in self.repo_root.glob(pattern):
                # Skip generated files, vendor directories, node_modules
                if any(x in str(path) for x in [
                    'node_modules', '.git', '__pycache__', 
                    'htmlcov', '.pytest_cache', '.venv'
                ]):
                    continue
                docs[key].append(path)
        
        return docs
    
    def check_readme_freshness(self, readme_path: Path) -> list[str]:
        """Check if README is fresh based on related code changes."""
        issues = []
        
        # Get directory of README
        readme_dir = readme_path.parent
        
        # Find Python files in same directory
        py_files = list(readme_dir.glob('*.py'))
        if not py_files and readme_dir != self.repo_root:
            py_files = list(readme_dir.glob('**/*.py'))
        
        if not py_files:
            return issues
        
        # Read README content
        try:
            readme_content = readme_path.read_text()
        except Exception as e:
            issues.append(f"Cannot read {readme_path}: {e}")
            return issues
        
        # Check for common issues
        if len(readme_content.strip()) < 100:
            issues.append(f"{readme_path}: README is too short (placeholder?)")
        
        # Check for outdated date patterns
        current_year = datetime.now().year
        if str(current_year - 1) in readme_content and str(current_year) not in readme_content:
            issues.append(f"{readme_path}: Contains last year's date, may be outdated")
        
        # Check for TODO markers
        if 'TODO' in readme_content or 'FIXME' in readme_content:
            issues.append(f"{readme_path}: Contains TODO/FIXME markers")
        
        return issues
    
    def check_agents_md_coverage(self, agents_path: Path) -> list[str]:
        """Check if AGENTS.md covers all important modules."""
        issues = []
        
        try:
            content = agents_path.read_text()
        except Exception as e:
            return [f"Cannot read {agents_path}: {e}"]
        
        # Check for critical modules that should be documented
        critical_dirs = [
            'src/codex/security',
            'src/codex/ast',
            'agents/',
            'scripts/agent',
        ]
        
        for crit_dir in critical_dirs:
            full_path = self.repo_root / crit_dir
            if full_path.exists() and crit_dir not in content:
                issues.append(
                    f"{agents_path}: Missing documentation for {crit_dir}"
                )
        
        # Check for recent update marker - flexible date check
        from datetime import datetime, timedelta
        today = datetime.now()
        last_6_months = [
            (today - timedelta(days=30 * i)).strftime('%Y-%m')
            for i in range(6)
        ]
        
        has_recent_date = any(date_str in content for date_str in last_6_months)
        if not has_recent_date:
            issues.append(
                f"{agents_path}: No recent update date "
                f"(expected one of: {', '.join(last_6_months[:3])}...)"
            )
        
        return issues
    
    def check_security_documentation(self) -> list[str]:
        """Check security-specific documentation requirements."""
        issues = []
        
        security_docs_dir = self.repo_root / 'docs' / 'security'
        required_docs = [
            'SECURITY_GUIDELINES.md',
            'README.md',
            'COMPLETE_STATUS_REPORT.md',
        ]
        
        for doc in required_docs:
            doc_path = security_docs_dir / doc
            if not doc_path.exists():
                issues.append(f"Missing required security doc: {doc}")
            else:
                # Check if it's substantial
                try:
                    content = doc_path.read_text()
                    if len(content) < 500:
                        issues.append(f"{doc}: Too short, needs expansion")
                except Exception as e:
                    issues.append(f"{doc}: Cannot read file - {e}")
        
        return issues
    
    def check_module_examples(self) -> list[str]:
        """Check that new modules have usage examples in docs."""
        issues = []
        
        # Check security module has examples
        security_init = self.repo_root / 'src' / 'codex' / 'security' / '__init__.py'
        if security_init.exists():
            # Check if examples exist in docs
            found_examples = False
            for doc_file in (self.repo_root / 'docs').rglob('*.md'):
                try:
                    content = doc_file.read_text()
                    if 'from codex.security import' in content:
                        found_examples = True
                        break
                except Exception:
                    # Cannot read file, skip it
                    continue
            
            if not found_examples:
                # Check README.md
                try:
                    readme = (self.repo_root / 'README.md').read_text()
                    if 'from codex.security import' not in readme:
                        issues.append(
                            "Security module missing usage examples in main README.md"
                        )
                except Exception:
                    # README.md check is best-effort; ignore errors reading this optional file.
                    pass
        
        return issues
    
    def generate_update_summary(self) -> str:
        """Generate a summary of required documentation updates."""
        summary = []
        summary.append("=" * 70)
        summary.append("DOCUMENTATION UPDATE REQUIREMENTS")
        summary.append("=" * 70)
        summary.append("")
        
        if not self.issues:
            summary.append("✅ All documentation is up to date!")
            return "\n".join(summary)
        
        summary.append(f"Found {len(self.issues)} documentation issues:\n")
        
        for i, issue in enumerate(self.issues, 1):
            summary.append(f"{i}. {issue}")
        
        summary.append("")
        summary.append("=" * 70)
        summary.append("RECOMMENDED ACTIONS")
        summary.append("=" * 70)
        summary.append("")
        summary.append("1. Update all README.md files with current information")
        summary.append("2. Add recent date markers (2025-12-23) to changed docs")
        summary.append("3. Document new modules with usage examples")
        summary.append("4. Remove TODO/FIXME markers or address them")
        summary.append("5. Update AGENTS.md with new capabilities")
        summary.append("")
        
        return "\n".join(summary)
    
    def run_checks(self) -> int:
        """Run all documentation checks."""
        print("🔍 Scanning repository for documentation...")
        
        docs = self.find_all_documentation()
        
        print(f"\nFound documentation files:")
        for doc_type, paths in docs.items():
            print(f"  {doc_type}: {len(paths)} files")
        
        print("\n📋 Running checks...\n")
        
        # Check all README files
        print("Checking README files...")
        for readme in docs['README']:
            issues = self.check_readme_freshness(readme)
            self.issues.extend(issues)
        
        # Check AGENTS.md files
        print("Checking AGENTS.md files...")
        for agents in docs['AGENTS']:
            issues = self.check_agents_md_coverage(agents)
            self.issues.extend(issues)
        
        # Check security documentation
        print("Checking security documentation...")
        issues = self.check_security_documentation()
        self.issues.extend(issues)
        
        # Check module examples
        print("Checking module examples...")
        issues = self.check_module_examples()
        self.issues.extend(issues)
        
        # Generate summary
        print("\n" + self.generate_update_summary())
        
        return len(self.issues)


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    checker = DocumentationChecker(repo_root)
    issue_count = checker.run_checks()
    
    if issue_count > 0:
        print(f"\n❌ Found {issue_count} documentation issues")
        print("Please update documentation before concluding work.")
        return 1
    else:
        print("\n✅ All documentation checks passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
