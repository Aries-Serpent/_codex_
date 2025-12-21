#!/usr/bin/env python3
"""
Code Change Self-Review Tool

Applies the autonomous self-review protocol to code changes,
ensuring comprehensive validation before committing.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import List, Set, Optional, Dict, Tuple
import ast
import re

from ai_self_review_protocol import (
    SelfReviewProtocol, Issue, IssueType, Priority, ReviewStatus
)


class CodeChangeReviewer:
    """Applies self-review protocol to code changes."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        self.protocol: Optional[SelfReviewProtocol] = None

    def get_changed_files(self) -> List[Path]:
        """Get list of changed files in the repository."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = [
                self.repo_path / line.strip()
                for line in result.stdout.split('\n')
                if line.strip()
            ]
            
            return [f for f in files if f.exists()]
            
        except subprocess.CalledProcessError:
            return []

    def analyze_python_file(self, filepath: Path) -> List[Tuple[IssueType, Priority, str]]:
        """Analyze a Python file for potential issues."""
        issues = []
        
        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))
            
            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(node):
                        if not node.name.startswith('_'):
                            issues.append((
                                IssueType.MISSING_DOC,
                                Priority.MEDIUM,
                                f"Missing docstring for {node.__class__.__name__} '{node.name}'"
                            ))
            
            # Check for TODOs and FIXMEs
            for i, line in enumerate(content.split('\n'), 1):
                if 'TODO' in line or 'FIXME' in line:
                    issues.append((
                        IssueType.INCOMPLETE,
                        Priority.MEDIUM,
                        f"Line {i}: Unresolved TODO/FIXME comment"
                    ))
            
            # Check for print statements (should use logging)
            if re.search(r'\bprint\s*\(', content):
                count = len(re.findall(r'\bprint\s*\(', content))
                if count > 2:  # Allow a few for scripts
                    issues.append((
                        IssueType.OPTIMIZATION,
                        Priority.LOW,
                        f"{count} print statements (consider using logging)"
                    ))
            
            # Check for bare except clauses
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append((
                            IssueType.RISK,
                            Priority.HIGH,
                            "Bare except clause can hide errors"
                        ))
            
        except (SyntaxError, UnicodeDecodeError) as e:
            issues.append((
                IssueType.RISK,
                Priority.CRITICAL,
                f"Syntax error or encoding issue: {e}"
            ))
        
        return issues

    def check_test_coverage(self, changed_files: List[Path]) -> List[Tuple[IssueType, Priority, str]]:
        """Check if changed source files have corresponding tests."""
        issues = []
        
        for filepath in changed_files:
            if not filepath.suffix == '.py':
                continue
            
            # Skip test files themselves
            if 'test' in filepath.name:
                continue
            
            # Check for corresponding test file
            relative = filepath.relative_to(self.repo_path)
            
            # Check common test patterns
            test_patterns = [
                Path(f"tests/test_{filepath.name}"),
                Path(f"tests/{filepath.parent.name}/test_{filepath.name}"),
                filepath.parent / f"test_{filepath.name}",
            ]
            
            has_test = any((self.repo_path / pattern).exists() for pattern in test_patterns)
            
            if not has_test:
                issues.append((
                    IssueType.MISSING_TEST,
                    Priority.HIGH,
                    f"No test file found for {relative}"
                ))
        
        return issues

    def check_documentation(self, changed_files: List[Path]) -> List[Tuple[IssueType, Priority, str]]:
        """Check if documentation needs updating."""
        issues = []
        
        # Check for Python files without README
        has_python = any(f.suffix == '.py' for f in changed_files)
        has_readme = any('README' in f.name for f in changed_files)
        
        if has_python and not has_readme:
            # Check if README exists
            readme_path = self.repo_path / "README.md"
            if not readme_path.exists():
                issues.append((
                    IssueType.MISSING_DOC,
                    Priority.HIGH,
                    "Repository lacks README.md"
                ))
        
        return issues

    def run_review_cycle(self, task_description: str) -> SelfReviewProtocol:
        """Run a complete self-review cycle on code changes."""
        # Initialize protocol
        self.protocol = SelfReviewProtocol(task_description)
        
        # Get changed files
        changed_files = self.get_changed_files()
        
        if not changed_files:
            print("No changed files to review")
            return self.protocol
        
        print(f"Reviewing {len(changed_files)} changed file(s)...\n")
        
        # Cycle 1: Initial analysis
        print("=== Cycle 1: Initial Analysis ===")
        cycle1 = self.protocol.start_cycle()
        
        for filepath in changed_files:
            print(f"Analyzing: {filepath.relative_to(self.repo_path)}")
            
            # Analyze Python files
            if filepath.suffix == '.py':
                file_issues = self.analyze_python_file(filepath)
                for issue_type, priority, description in file_issues:
                    self.protocol.identify_issue(
                        issue_type,
                        priority,
                        description,
                        str(filepath.relative_to(self.repo_path))
                    )
        
        # Check test coverage
        test_issues = self.check_test_coverage(changed_files)
        for issue_type, priority, description in test_issues:
            self.protocol.identify_issue(
                issue_type,
                priority,
                description,
                "test_coverage"
            )
        
        # Check documentation
        doc_issues = self.check_documentation(changed_files)
        for issue_type, priority, description in doc_issues:
            self.protocol.identify_issue(
                issue_type,
                priority,
                description,
                "documentation"
            )
        
        changes = [f"Analyzed {len(changed_files)} files"]
        self.protocol.complete_cycle(changes)
        
        print(f"Issues identified: {len(self.protocol.all_issues)}\n")
        
        # Cycle 2: Convergence check
        print("=== Cycle 2: Convergence Check ===")
        cycle2 = self.protocol.start_cycle()
        
        converged, reason = self.protocol.check_convergence()
        print(f"Convergence status: {reason}\n")
        
        self.protocol.complete_cycle(["Performed convergence check"])
        
        # Finalize
        final_notes = f"Reviewed {len(changed_files)} changed files with {len(self.protocol.all_issues)} issues identified"
        self.protocol.finalize_review(final_notes)
        
        return self.protocol


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Change Self-Review Tool")
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                       help="Repository path")
    parser.add_argument("--task", default="Code change review",
                       help="Task description")
    parser.add_argument("--output", type=Path,
                       help="Output directory for reports")
    parser.add_argument("--save-report", action="store_true",
                       help="Save review report to disk")
    
    args = parser.parse_args()
    
    # Run review
    reviewer = CodeChangeReviewer(args.repo)
    protocol = reviewer.run_review_cycle(args.task)
    
    # Print summary
    protocol.print_summary()
    
    # Save report if requested
    if args.save_report:
        if args.output:
            protocol.output_dir = args.output
        report_path = protocol.save_report()
        print(f"\n✓ Report saved: {report_path}")
    
    # Exit with non-zero if not production ready
    return 0 if protocol.report.production_ready else 1


if __name__ == "__main__":
    sys.exit(main())
