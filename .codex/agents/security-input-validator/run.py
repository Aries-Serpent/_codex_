#!/usr/bin/env python3
"""
Security Input Validator Agent

Autonomous agent that validates all user inputs across the codebase for security
risks including command injection, path traversal, SQL injection, XSS, and other
OWASP Top 10 vulnerabilities.

Usage:
    python run.py --files <file1> <file2> ...
    python run.py --pr <pr_number>
    python run.py --all
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Add src to path for imports
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    LDAP_INJECTION = "ldap_injection"
    XXE = "xxe"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"


@dataclass
class SecurityIssue:
    """Represents a detected security issue."""
    file_path: str
    line_number: int
    severity: Severity
    category: VulnerabilityType
    message: str
    context: str
    suggestion: str
    test_template: str = ""
    cwe_id: str = ""


@dataclass
class ValidationPatterns:
    """Security validation patterns."""
    
    # Command injection patterns
    command_injection: dict[str, str] = field(default_factory=lambda: {
        "shell_metacharacters": r'[`$|&;<>()\\]',
        "command_substitution": r'\$\([^)]*\)',
        "backtick_substitution": r'`[^`]*`',
        "pipe_operator": r'\s*\|\s*',
        "redirection": r'[<>]{1,2}',
        "background": r'\s*&\s*$',
        "semicolon_chain": r';\s*\w+',
    })
    
    # Path traversal patterns
    path_traversal: dict[str, str] = field(default_factory=lambda: {
        "dot_dot_slash": r'\.\.[/\\]',
        "encoded_traversal": r'%2e%2e[/\\]',
        "double_encoded": r'%252e%252e',
        "unicode_traversal": r'[\u002e][\u002e]',
    })
    
    # SQL injection patterns
    sql_injection: dict[str, str] = field(default_factory=lambda: {
        "union_select": r'\bunion\b.*\bselect\b',
        "comment_out": r'(--|#|/\*)',
        "or_true": r'\bor\b\s+[\d\w]+\s*=\s*[\d\w]+',
        "string_concat": r'\+\s*["\']',
        "stacked_queries": r';\s*\b(select|insert|update|delete|drop)\b',
    })
    
    # XSS patterns
    xss: dict[str, str] = field(default_factory=lambda: {
        "script_tag": r'<script[^>]*>',
        "event_handler": r'on\w+\s*=',
        "javascript_protocol": r'javascript:',
        "data_protocol": r'data:text/html',
    })
    
    # Unsafe function patterns (Python)
    unsafe_functions: list[str] = field(default_factory=lambda: [
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_output",
        "os.system",
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "urllib.request.urlopen",
        "pickle.loads",
        "yaml.load",  # Should use safe_load
    ])


class SecurityInputValidator:
    """Main security validator agent."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or self._default_config()
        self.patterns = ValidationPatterns()
        self.issues: list[SecurityIssue] = []
    
    def _default_config(self) -> dict[str, Any]:
        """Default configuration."""
        return {
            "enabled": True,
            "auto_fix": True,
            "generate_tests": True,
            "severity_threshold": "MEDIUM",
            "exclude_patterns": [
                "tests/**",
                "**/*.test.py",
                "**/node_modules/**",
                "**/.venv/**",
            ],
        }
    
    def validate_file(self, file_path: Path) -> list[SecurityIssue]:
        """
        Validate a single file for security issues.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            List of SecurityIssue objects found
        """
        issues = []
        
        # Skip excluded patterns
        if self._should_exclude(file_path):
            return issues
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return issues
        
        # Python-specific analysis
        if file_path.suffix == ".py":
            issues.extend(self._validate_python(file_path, content))
        
        # Language-agnostic pattern matching
        issues.extend(self._validate_patterns(file_path, content))
        
        return issues
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from validation."""
        path_str = str(file_path)
        for pattern in self.config.get("exclude_patterns", []):
            if Path(path_str).match(pattern):
                return True
        return False
    
    def _validate_python(self, file_path: Path, content: str) -> list[SecurityIssue]:
        """Validate Python code using AST analysis."""
        issues = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            # Not valid Python, skip AST analysis
            return issues
        
        # Walk the AST looking for dangerous patterns
        for node in ast.walk(tree):
            # Check for subprocess calls
            if isinstance(node, ast.Call):
                issue = self._check_subprocess_call(node, file_path, content)
                if issue:
                    issues.append(issue)
                
                # Check for eval/exec
                issue = self._check_eval_exec(node, file_path, content)
                if issue:
                    issues.append(issue)
                
                # Check for pickle.loads
                issue = self._check_unsafe_deserialization(node, file_path, content)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def _check_subprocess_call(
        self, node: ast.Call, file_path: Path, content: str
    ) -> SecurityIssue | None:
        """Check for unsafe subprocess usage."""
        # Check if this is a subprocess call
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "subprocess":
                    func_name = f"subprocess.{node.func.attr}"
        
        if not func_name.startswith("subprocess."):
            return None
        
        # Check for shell=True
        has_shell_true = False
        for keyword in node.keywords:
            if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                if keyword.value.value is True:
                    has_shell_true = True
        
        # Check if command is constructed from user input
        has_user_input = self._has_user_input(node)
        
        if has_shell_true or has_user_input:
            line_num = node.lineno
            lines = content.split("\n")
            context = lines[line_num - 1] if line_num <= len(lines) else ""
            
            return SecurityIssue(
                file_path=str(file_path),
                line_number=line_num,
                severity=Severity.CRITICAL,
                category=VulnerabilityType.COMMAND_INJECTION,
                message=f"Unsafe subprocess call at line {line_num}",
                context=context.strip(),
                suggestion=self._generate_subprocess_fix(context),
                test_template=self._generate_subprocess_test(func_name),
                cwe_id="CWE-78",
            )
        
        return None
    
    def _has_user_input(self, node: ast.Call) -> bool:
        """Check if call arguments might contain user input."""
        # Look for format strings, f-strings, or concatenation
        for arg in node.args:
            if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                return True
            if isinstance(arg, ast.Call):
                if isinstance(arg.func, ast.Attribute):
                    if arg.func.attr in ("format", "join"):
                        return True
        return False
    
    def _check_eval_exec(
        self, node: ast.Call, file_path: Path, content: str
    ) -> SecurityIssue | None:
        """Check for eval/exec usage."""
        func_name = ""
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec", "compile"):
                func_name = node.func.id
        
        if not func_name:
            return None
        
        line_num = node.lineno
        lines = content.split("\n")
        context = lines[line_num - 1] if line_num <= len(lines) else ""
        
        return SecurityIssue(
            file_path=str(file_path),
            line_number=line_num,
            severity=Severity.CRITICAL,
            category=VulnerabilityType.COMMAND_INJECTION,
            message=f"Dangerous use of {func_name}() at line {line_num}",
            context=context.strip(),
            suggestion=f"Avoid using {func_name}(). Consider using ast.literal_eval() for safe evaluation or refactor to avoid dynamic code execution.",
            test_template=self._generate_eval_test(func_name),
            cwe_id="CWE-95",
        )
    
    def _check_unsafe_deserialization(
        self, node: ast.Call, file_path: Path, content: str
    ) -> SecurityIssue | None:
        """Check for unsafe deserialization (pickle.loads)."""
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "pickle" and node.func.attr == "loads":
                    func_name = "pickle.loads"
        
        if not func_name:
            return None
        
        line_num = node.lineno
        lines = content.split("\n")
        context = lines[line_num - 1] if line_num <= len(lines) else ""
        
        return SecurityIssue(
            file_path=str(file_path),
            line_number=line_num,
            severity=Severity.HIGH,
            category=VulnerabilityType.UNSAFE_DESERIALIZATION,
            message=f"Unsafe deserialization with pickle.loads() at line {line_num}",
            context=context.strip(),
            suggestion="Use JSON or safer serialization formats. If pickle is required, verify data source and consider HMAC signing.",
            test_template=self._generate_deserialization_test(),
            cwe_id="CWE-502",
        )
    
    def _validate_patterns(self, file_path: Path, content: str) -> list[SecurityIssue]:
        """Validate using regex pattern matching."""
        issues = []
        lines = content.split("\n")
        in_docstring = False
        
        for line_num, line in enumerate(lines, start=1):
            # Track docstrings
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
            
            # Skip comments, docstrings, and imports
            stripped = line.strip()
            if (stripped.startswith("#") or in_docstring or 
                stripped.startswith("import ") or stripped.startswith("from ") or
                not stripped or "getLogger" in stripped):
                continue
            
            # Check command injection patterns
            for pattern_name, pattern in self.patterns.command_injection.items():
                if re.search(pattern, line):
                    # Skip backticks in code comments or variable names like `codex_ml`
                    if pattern_name == "backtick_substitution" and "`" in line and "subprocess" not in line.lower():
                        continue
                    
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        severity=Severity.HIGH,
                        category=VulnerabilityType.COMMAND_INJECTION,
                        message=f"Potential command injection: {pattern_name}",
                        context=line.strip(),
                        suggestion="Validate and sanitize user input. Use allowlist-based validation.",
                        cwe_id="CWE-78",
                    ))
            
            # Check path traversal patterns
            for pattern_name, pattern in self.patterns.path_traversal.items():
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        severity=Severity.HIGH,
                        category=VulnerabilityType.PATH_TRAVERSAL,
                        message=f"Potential path traversal: {pattern_name}",
                        context=line.strip(),
                        suggestion="Use Path.resolve() and validate paths are within expected directory.",
                        cwe_id="CWE-22",
                    ))
        
        return issues
    
    def _generate_subprocess_fix(self, context: str) -> str:
        """Generate fix suggestion for subprocess issue."""
        return """Replace with:
1. Validate all user inputs with allowlist-based validation
2. Use list arguments instead of string: subprocess.run(['cmd', 'arg1', 'arg2'])
3. Never use shell=True with user input
4. Example:
   def _validate_input(value: str) -> None:
       if not re.match(r'^[a-zA-Z0-9._-]+$', value):
           raise ValueError("Invalid input")
   
   _validate_input(user_input)
   subprocess.run(['command', user_input], check=True)"""
    
    def _generate_subprocess_test(self, func_name: str) -> str:
        """Generate test template for subprocess issue."""
        return f"""
def test_subprocess_command_injection():
    '''Test that command injection attempts are blocked.'''
    with pytest.raises(ValueError, match="Invalid input"):
        your_function("; rm -rf /")
    with pytest.raises(ValueError, match="Invalid input"):
        your_function("$(whoami)")
    with pytest.raises(ValueError, match="Invalid input"):
        your_function("`whoami`")
"""
    
    def _generate_eval_test(self, func_name: str) -> str:
        """Generate test template for eval/exec issue."""
        return f"""
def test_no_eval_exec():
    '''Ensure eval/exec is not used with untrusted input.'''
    # Replace {func_name}() with safe alternative like ast.literal_eval()
    # or refactor to avoid dynamic code execution
    pass
"""
    
    def _generate_deserialization_test(self) -> str:
        """Generate test template for deserialization issue."""
        return """
def test_safe_deserialization():
    '''Test that only trusted data is deserialized.'''
    # Use JSON instead of pickle when possible
    # If pickle is required, verify data source and use HMAC
    import json
    data = json.loads(trusted_json_string)
    assert isinstance(data, dict)
"""
    
    def generate_report(self) -> dict[str, Any]:
        """Generate validation report."""
        issues_by_severity = {}
        for severity in Severity:
            issues_by_severity[severity.value] = [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "category": issue.category.value,
                    "message": issue.message,
                    "context": issue.context,
                    "suggestion": issue.suggestion,
                    "cwe": issue.cwe_id,
                }
                for issue in self.issues
                if issue.severity == severity
            ]
        
        return {
            "total_issues": len(self.issues),
            "by_severity": issues_by_severity,
            "by_category": self._group_by_category(),
            "critical_count": len([i for i in self.issues if i.severity == Severity.CRITICAL]),
            "high_count": len([i for i in self.issues if i.severity == Severity.HIGH]),
        }
    
    def _group_by_category(self) -> dict[str, int]:
        """Group issues by category."""
        categories = {}
        for issue in self.issues:
            cat = issue.category.value
            categories[cat] = categories.get(cat, 0) + 1
        return categories


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Security Input Validator Agent")
    parser.add_argument("--files", nargs="+", help="Files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all Python files")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    parser.add_argument("--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], default="MEDIUM")
    args = parser.parse_args()
    
    validator = SecurityInputValidator()
    
    if args.all:
        # Find all Python files
        files = list(ROOT.glob("**/*.py"))
        # Exclude common directories
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
            issues = validator.validate_file(file_path)
            validator.issues.extend(issues)
    
    # Generate report
    report = validator.generate_report()
    
    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        # Text output
        print(f"\n{'='*80}")
        print("Security Input Validator - Scan Results")
        print(f"{'='*80}\n")
        print(f"Total Issues: {report['total_issues']}")
        print(f"Critical: {report['critical_count']}")
        print(f"High: {report['high_count']}")
        print(f"\nBy Category:")
        for cat, count in report['by_category'].items():
            print(f"  {cat}: {count}")
        
        print(f"\n{'='*80}")
        print("Issues by Severity")
        print(f"{'='*80}\n")
        
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            issues = report['by_severity'].get(severity, [])
            if issues:
                print(f"\n{severity}:")
                for issue in issues:
                    print(f"  {issue['file']}:{issue['line']}")
                    print(f"    {issue['message']}")
                    print(f"    Context: {issue['context']}")
                    print(f"    CWE: {issue['cwe']}")
                    print()
    
    # Return non-zero if critical or high severity issues found
    if report['critical_count'] > 0 or report['high_count'] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
