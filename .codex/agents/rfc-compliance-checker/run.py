#!/usr/bin/env python3
"""
RFC Compliance Checker Agent

Ensures standards compliance across HTTP, URL, and protocol implementations.
Validates against RFC 3986 (URI), RFC 7230-7235 (HTTP/1.1), RFC 6265 (Cookies).

Usage:
    python run.py --files <file1> <file2> ...
    python run.py --all
    python run.py --check-uri
    python run.py --check-http
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


class RFCStandard(Enum):
    """RFC standards to check."""
    RFC_3986 = "RFC 3986: URI Generic Syntax"
    RFC_7230 = "RFC 7230: HTTP/1.1 Message Syntax"
    RFC_7231 = "RFC 7231: HTTP/1.1 Semantics"
    RFC_6265 = "RFC 6265: HTTP State Management (Cookies)"
    RFC_2616 = "RFC 2616: HTTP/1.1 (obsolete, check for updates)"


class ComplianceLevel(Enum):
    """Compliance check severity."""
    ERROR = "ERROR"        # Non-compliant, must fix
    WARNING = "WARNING"    # Deviation from standard
    INFO = "INFO"          # Suggestion for improvement


@dataclass
class ComplianceIssue:
    """Represents an RFC compliance issue."""
    file_path: str
    line_number: int
    level: ComplianceLevel
    standard: RFCStandard
    message: str
    context: str
    suggestion: str
    reference: str  # Link to RFC section


class RFCComplianceChecker:
    """Main RFC compliance checker agent."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or self._default_config()
        self.issues: list[ComplianceIssue] = []
        
        # RFC 3986 patterns
        self.uri_patterns = {
            "scheme_case_sensitive": r'([a-z]+)://(?:[A-Z])',
            "scheme_comparison": r'\.scheme\s*[!=]=\s*["\']https?["\']',
            "manual_url_parse": r'\.split\(["\'][:/]+["\']\)',
        }
        
        # HTTP header patterns (RFC 7230)
        self.http_header_patterns = {
            "header_case_sensitive": r'headers?\[["\'][A-Z][a-z-]+["\']\]',
            "custom_header_format": r'["\']X-[A-Z][a-z-]*["\']',
        }
    
    def _default_config(self) -> dict[str, Any]:
        """Default configuration."""
        return {
            "enabled": True,
            "check_uri": True,
            "check_http": True,
            "check_cookies": True,
            "exclude_patterns": ["tests/**", "**/node_modules/**"],
        }
    
    def validate_file(self, file_path: Path) -> list[ComplianceIssue]:
        """Validate a file for RFC compliance issues."""
        issues = []
        
        if self._should_exclude(file_path):
            return issues
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return issues
        
        # Python-specific checks
        if file_path.suffix == ".py":
            issues.extend(self._validate_python_uri(file_path, content))
            issues.extend(self._validate_python_http(file_path, content))
        
        return issues
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded."""
        path_str = str(file_path)
        for pattern in self.config.get("exclude_patterns", []):
            if Path(path_str).match(pattern):
                return True
        return False
    
    def _validate_python_uri(self, file_path: Path, content: str) -> list[ComplianceIssue]:
        """Validate URI handling against RFC 3986."""
        issues = []
        lines = content.split("\n")
        
        # Check for case-sensitive scheme comparison (RFC 3986 §3.1)
        for line_num, line in enumerate(lines, start=1):
            # Pattern: parsed.scheme == "https" (should use .lower())
            if re.search(r'\.scheme\s*[!=]=\s*["\']https?["\']', line):
                if ".lower()" not in line:
                    issues.append(ComplianceIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        level=ComplianceLevel.ERROR,
                        standard=RFCStandard.RFC_3986,
                        message="Case-sensitive URI scheme comparison violates RFC 3986",
                        context=line.strip(),
                        suggestion="Use .lower() for scheme comparison: parsed.scheme.lower() == 'https'",
                        reference="https://tools.ietf.org/html/rfc3986#section-3.1",
                    ))
            
            # Check for manual URL parsing (should use urllib.parse)
            if "urlparse" not in content and re.search(r'\.split\(["\'][:/]+["\']\)', line):
                if "http://" in line or "https://" in line:
                    issues.append(ComplianceIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        level=ComplianceLevel.WARNING,
                        standard=RFCStandard.RFC_3986,
                        message="Manual URL parsing should use urllib.parse.urlparse()",
                        context=line.strip(),
                        suggestion="Use urllib.parse.urlparse() for RFC-compliant URL parsing",
                        reference="https://tools.ietf.org/html/rfc3986",
                    ))
            
            # Check for missing hostname validation
            if "urlparse" in line and "hostname" not in content[max(0, content.find(line)-500):content.find(line)+500]:
                if line_num < len(lines) - 5:  # Look ahead a few lines
                    next_lines = "\n".join(lines[line_num:line_num+5])
                    if "hostname" not in next_lines:
                        issues.append(ComplianceIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            level=ComplianceLevel.WARNING,
                            standard=RFCStandard.RFC_3986,
                            message="URL parsing should validate hostname presence",
                            context=line.strip(),
                            suggestion="Add validation: if not parsed.hostname: raise ValueError('Invalid URL')",
                            reference="https://tools.ietf.org/html/rfc3986#section-3.2.2",
                        ))
        
        # AST-based checks for urllib usage
        try:
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    issue = self._check_urllib_usage(node, file_path, content)
                    if issue:
                        issues.append(issue)
        except SyntaxError:
            pass
        
        return issues
    
    def _check_urllib_usage(
        self, node: ast.Call, file_path: Path, content: str
    ) -> ComplianceIssue | None:
        """Check urllib usage for RFC compliance."""
        # Check for urlparse usage
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                if (hasattr(node.func.value.value, 'id') and 
                    node.func.value.value.id == "urllib" and
                    node.func.value.attr == "parse" and
                    node.func.attr == "urlparse"):
                    # Found urlparse usage, check for scheme validation
                    return None  # This is good, just ensure validation follows
        
        return None
    
    def _validate_python_http(self, file_path: Path, content: str) -> list[ComplianceIssue]:
        """Validate HTTP handling against RFC 7230-7235."""
        issues = []
        lines = content.split("\n")
        
        for line_num, line in enumerate(lines, start=1):
            # Check for case-sensitive header comparison (RFC 7230 §3.2)
            # Headers are case-insensitive
            if re.search(r'headers?\[["\'][A-Z][a-z-]+["\']\]\s*[!=]=', line):
                if ".lower()" not in line and ".casefold()" not in line:
                    issues.append(ComplianceIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        level=ComplianceLevel.WARNING,
                        standard=RFCStandard.RFC_7230,
                        message="HTTP headers should be compared case-insensitively",
                        context=line.strip(),
                        suggestion="Use .lower() or .casefold() for header comparison, or use requests/httpx which handle this",
                        reference="https://tools.ietf.org/html/rfc7230#section-3.2",
                    ))
            
            # Check for obsolete RFC 2616 references
            if "RFC 2616" in line or "rfc2616" in line.lower():
                issues.append(ComplianceIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    level=ComplianceLevel.INFO,
                    standard=RFCStandard.RFC_2616,
                    message="RFC 2616 is obsolete, replaced by RFC 7230-7235",
                    context=line.strip(),
                    suggestion="Update references to RFC 7230 (Message Syntax), RFC 7231 (Semantics), etc.",
                    reference="https://tools.ietf.org/html/rfc7230",
                ))
            
            # Check for custom header naming (RFC 7231 §8.3.1)
            if re.search(r'["\']X-[A-Z][a-z-]*["\']', line):
                issues.append(ComplianceIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    level=ComplianceLevel.INFO,
                    standard=RFCStandard.RFC_7231,
                    message="X- prefix for custom headers is deprecated (RFC 6648)",
                    context=line.strip(),
                    suggestion="Use a descriptive name without X- prefix, or register with IANA",
                    reference="https://tools.ietf.org/html/rfc6648",
                ))
            
            # Check for missing User-Agent (RFC 7231 §5.5.3)
            if "urllib.request.Request" in line or "requests.get" in line:
                # Look for User-Agent in nearby lines
                context_start = max(0, line_num - 5)
                context_end = min(len(lines), line_num + 5)
                context_lines = lines[context_start:context_end]
                if not any("User-Agent" in l for l in context_lines):
                    issues.append(ComplianceIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        level=ComplianceLevel.WARNING,
                        standard=RFCStandard.RFC_7231,
                        message="HTTP requests should include User-Agent header",
                        context=line.strip(),
                        suggestion="Add User-Agent header: headers={'User-Agent': 'YourApp/1.0'}",
                        reference="https://tools.ietf.org/html/rfc7231#section-5.5.3",
                    ))
        
        return issues
    
    def generate_report(self) -> dict[str, Any]:
        """Generate compliance report."""
        issues_by_level = {}
        for level in ComplianceLevel:
            issues_by_level[level.value] = [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "standard": issue.standard.value,
                    "message": issue.message,
                    "context": issue.context,
                    "suggestion": issue.suggestion,
                    "reference": issue.reference,
                }
                for issue in self.issues
                if issue.level == level
            ]
        
        issues_by_standard = {}
        for standard in RFCStandard:
            count = len([i for i in self.issues if i.standard == standard])
            if count > 0:
                issues_by_standard[standard.value] = count
        
        return {
            "total_issues": len(self.issues),
            "by_level": issues_by_level,
            "by_standard": issues_by_standard,
            "error_count": len([i for i in self.issues if i.level == ComplianceLevel.ERROR]),
            "warning_count": len([i for i in self.issues if i.level == ComplianceLevel.WARNING]),
        }
    
    def generate_fixes(self) -> list[dict[str, Any]]:
        """Generate automatic fixes for compliance issues."""
        fixes = []
        
        for issue in self.issues:
            if issue.level == ComplianceLevel.ERROR:
                fix = self._generate_fix(issue)
                if fix:
                    fixes.append(fix)
        
        return fixes
    
    def _generate_fix(self, issue: ComplianceIssue) -> dict[str, Any] | None:
        """Generate a fix for a specific issue."""
        if "Case-sensitive URI scheme" in issue.message:
            # Fix: Add .lower() to scheme comparison
            old_line = issue.context
            if ".scheme ==" in old_line:
                new_line = old_line.replace(".scheme ==", ".scheme.lower() ==")
            elif ".scheme !=" in old_line:
                new_line = old_line.replace(".scheme !=", ".scheme.lower() !=")
            else:
                return None
            
            return {
                "file": issue.file_path,
                "line": issue.line_number,
                "old": old_line,
                "new": new_line,
                "description": "Add .lower() for RFC 3986 compliant scheme comparison",
            }
        
        return None


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RFC Compliance Checker Agent")
    parser.add_argument("--files", nargs="+", help="Files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all Python files")
    parser.add_argument("--check-uri", action="store_true", help="Check URI compliance (RFC 3986)")
    parser.add_argument("--check-http", action="store_true", help="Check HTTP compliance (RFC 7230-7235)")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    parser.add_argument("--auto-fix", action="store_true", help="Generate automatic fixes")
    args = parser.parse_args()
    
    config = {}
    if args.check_uri:
        config["check_http"] = False
        config["check_cookies"] = False
    if args.check_http:
        config["check_uri"] = False
        config["check_cookies"] = False
    
    checker = RFCComplianceChecker(config)
    
    if args.all:
        files = list(ROOT.glob("**/*.py"))
        files = [
            f for f in files
            if not any(part in f.parts for part in [".venv", "venv", "node_modules", ".git"])
        ]
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        print("Error: Specify --files or --all", file=sys.stderr)
        return 1
    
    # Validate files
    for file_path in files:
        if file_path.exists() and file_path.is_file():
            issues = checker.validate_file(file_path)
            checker.issues.extend(issues)
    
    # Generate report
    report = checker.generate_report()
    
    if args.output == "json":
        output = report
        if args.auto_fix:
            output["fixes"] = checker.generate_fixes()
        print(json.dumps(output, indent=2))
    else:
        # Text output
        print(f"\n{'='*80}")
        print("RFC Compliance Checker - Scan Results")
        print(f"{'='*80}\n")
        print(f"Total Issues: {report['total_issues']}")
        print(f"Errors: {report['error_count']}")
        print(f"Warnings: {report['warning_count']}")
        
        if report['by_standard']:
            print(f"\nBy RFC Standard:")
            for standard, count in report['by_standard'].items():
                print(f"  {standard}: {count}")
        
        print(f"\n{'='*80}")
        print("Issues by Level")
        print(f"{'='*80}\n")
        
        for level in ["ERROR", "WARNING", "INFO"]:
            issues = report['by_level'].get(level, [])
            if issues:
                print(f"\n{level}:")
                for issue in issues:
                    print(f"  {issue['file']}:{issue['line']}")
                    print(f"    {issue['message']}")
                    print(f"    Standard: {issue['standard']}")
                    print(f"    Context: {issue['context']}")
                    print(f"    Suggestion: {issue['suggestion']}")
                    print(f"    Reference: {issue['reference']}")
                    print()
        
        if args.auto_fix:
            fixes = checker.generate_fixes()
            if fixes:
                print(f"\n{'='*80}")
                print("Automatic Fixes Available")
                print(f"{'='*80}\n")
                for fix in fixes:
                    print(f"  {fix['file']}:{fix['line']}")
                    print(f"    {fix['description']}")
                    print(f"    - {fix['old']}")
                    print(f"    + {fix['new']}")
                    print()
    
    # Return non-zero if errors found
    if report['error_count'] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
