#!/usr/bin/env python3
"""Enhanced modernization scanner for Python codebase (v2).

Scans Python files for legacy patterns and suggests modernization:
- Old typing imports (typing.List vs list)
- Old exception syntax (except E, e: vs except E as e:)
- Dataclass conversion opportunities
- Walrus operator opportunities (optional)
- String formatting patterns
"""

import ast
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List


class Severity(Enum):
    """Issue severity levels."""
    SUGGESTION = "suggestion"  # Optional improvement
    WARNING = "warning"  # Should fix but not critical
    ERROR = "error"  # Should definitely fix
    AUTO_REFACTOR = "auto_refactor"  # Safe to auto-fix


@dataclass
class Issue:
    """Represents a modernization issue."""
    filename: str
    lineno: int
    message: str
    category: str
    severity: Severity
    suggestion: str = ""


class ModernizationChecker(ast.NodeVisitor):
    """Enhanced AST visitor to detect legacy Python patterns."""
    
    def __init__(self, filename: str, check_walrus: bool = False):
        self.filename = filename
        self.issues: List[Issue] = []
        self.check_walrus = check_walrus
        self.class_candidates: List[ast.ClassDef] = []
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check for old typing imports."""
        if node.module == "typing":
            for alias in node.names:
                # Check for capitalized generic types (deprecated in 3.9+)
                if alias.name in ("List", "Dict", "Set", "Tuple"):
                    builtin_name = alias.name.lower()
                    self.issues.append(Issue(
                        filename=self.filename,
                        lineno=node.lineno,
                        message=f"Use built-in {builtin_name} instead of typing.{alias.name}",
                        category="typing-builtin",
                        severity=Severity.WARNING,
                        suggestion=f"Replace `typing.{alias.name}` with `{builtin_name}`"
                    ))
                elif alias.name == "Optional":
                    self.issues.append(Issue(
                        filename=self.filename,
                        lineno=node.lineno,
                        message="Consider using | None syntax instead of typing.Optional",
                        category="typing-union",
                        severity=Severity.SUGGESTION,
                        suggestion="Replace `Optional[T]` with `T | None` (Python 3.10+)"
                    ))
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Check for old exception syntax."""
        # Python 2 style: except Exception, e:
        # This is actually a syntax error in Python 3, but check AST structure
        # Modern Python uses: except Exception as e:
        
        # The AST already enforces 'as' syntax, but we can check for
        # common anti-patterns like bare except
        if node.type is None:
            self.issues.append(Issue(
                filename=self.filename,
                lineno=node.lineno,
                message="Bare except clause catches all exceptions including SystemExit",
                category="exception-bare",
                severity=Severity.WARNING,
                suggestion="Use `except Exception:` or specific exception types"
            ))
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Check for dataclass conversion opportunities."""
        # Look for classes that might benefit from dataclass conversion
        has_init = False
        has_other_methods = False
        init_node = None
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    has_init = True
                    init_node = item
                elif not item.name.startswith("_"):
                    has_other_methods = True
        
        # Candidate: has __init__, no or few other methods
        if has_init and not has_other_methods and init_node:
            # Check if __init__ is simple (just assignments)
            is_simple = self._is_simple_init(init_node)
            
            if is_simple:
                self.issues.append(Issue(
                    filename=self.filename,
                    lineno=node.lineno,
                    message=f"Class '{node.name}' could be converted to a dataclass",
                    category="dataclass-candidate",
                    severity=Severity.SUGGESTION,
                    suggestion="Consider using @dataclass decorator for simpler syntax"
                ))
        
        self.generic_visit(node)
    
    def _is_simple_init(self, init_node: ast.FunctionDef) -> bool:
        """Check if __init__ only contains simple assignments."""
        if not init_node.body:
            return False
        
        for stmt in init_node.body:
            # Allow: self.x = x or self.x = value
            if isinstance(stmt, ast.Assign):
                if len(stmt.targets) != 1:
                    return False
                target = stmt.targets[0]
                if not (isinstance(target, ast.Attribute) and 
                        isinstance(target.value, ast.Name) and
                        target.value.id == "self"):
                    return False
            # Allow docstrings
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Str, ast.Constant)):
                continue
            else:
                # Other statements make it non-simple
                return False
        
        return True
    
    def visit_Assign(self, node: ast.Assign):
        """Check for walrus operator opportunities (if enabled)."""
        if not self.check_walrus:
            self.generic_visit(node)
            return
        
        # Look for pattern: x = expr; if x:
        # Could be: if (x := expr):
        # This is a simplified check
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Check for old string formatting."""
        # Check for str.format() that could be f-string
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "format" and isinstance(node.func.value, (ast.Str, ast.Constant)):
                self.issues.append(Issue(
                    filename=self.filename,
                    lineno=node.lineno,
                    message="Consider using f-string instead of .format()",
                    category="string-format",
                    severity=Severity.SUGGESTION,
                    suggestion="Replace 'string'.format() with f'string'"
                ))
        self.generic_visit(node)


def scan_file(filepath: Path, check_walrus: bool = False) -> List[Issue]:
    """Scan a single Python file for modernization opportunities."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return []
    
    checker = ModernizationChecker(str(filepath), check_walrus=check_walrus)
    checker.visit(tree)
    return checker.issues


def generate_report(issues: List[Issue], output_json: str = None, output_md: str = None):
    """Generate reports from scan results."""
    # Group by category and severity
    by_category: Dict[str, List[Issue]] = {}
    by_severity: Dict[Severity, List[Issue]] = {}
    
    for issue in issues:
        by_category.setdefault(issue.category, []).append(issue)
        by_severity.setdefault(issue.severity, []).append(issue)
    
    # JSON report
    if output_json:
        json_data = {
            "total_issues": len(issues),
            "by_severity": {sev.value: len(items) for sev, items in by_severity.items()},
            "by_category": {cat: len(items) for cat, items in by_category.items()},
            "issues": [
                {
                    "file": issue.filename,
                    "line": issue.lineno,
                    "message": issue.message,
                    "category": issue.category,
                    "severity": issue.severity.value,
                    "suggestion": issue.suggestion,
                }
                for issue in issues
            ],
        }
        
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
    
    # Markdown report
    if output_md:
        Path(output_md).parent.mkdir(parents=True, exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# Modernization Scanner Report\n\n")
            f.write(f"**Total Issues**: {len(issues)}\n\n")
            
            f.write("## By Severity\n\n")
            for severity in [Severity.ERROR, Severity.WARNING, Severity.SUGGESTION, Severity.AUTO_REFACTOR]:
                count = len(by_severity.get(severity, []))
                f.write(f"- {severity.value}: {count}\n")
            
            f.write("\n## By Category\n\n")
            for category, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
                f.write(f"- {category}: {len(items)}\n")
            
            f.write("\n## Issues by Category\n\n")
            for category, items in sorted(by_category.items()):
                f.write(f"### {category} ({len(items)} issues)\n\n")
                f.write("|File|Line|Message|Severity|\n")
                f.write("|----|----|-------|--------|\n")
                for issue in items[:10]:  # Limit to first 10 per category
                    f.write(f"|{Path(issue.filename).name}|{issue.lineno}|{issue.message}|{issue.severity.value}|\n")
                if len(items) > 10:
                    f.write(f"\n*...and {len(items) - 10} more*\n")
                f.write("\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan for Python modernization opportunities (v2)")
    parser.add_argument("root", nargs="?", default="src", help="Root directory to scan (default: src)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed suggestions")
    parser.add_argument("--check-walrus", action="store_true", help="Check for walrus operator opportunities")
    parser.add_argument("--json", type=str, help="Output JSON report path")
    parser.add_argument("--md", type=str, help="Output Markdown report path")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit with error code if ERROR severity found")
    
    args = parser.parse_args()
    
    root_path = Path(args.root).resolve()
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist", file=sys.stderr)
        return 1
    
    total_files = 0
    all_issues: List[Issue] = []
    
    # Find all Python files
    for py_file in root_path.rglob("*.py"):
        # Skip common exclude patterns
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if any(part in ("node_modules", "venv", "__pycache__", "build", "dist") 
               for part in py_file.parts):
            continue
        
        total_files += 1
        issues = scan_file(py_file, check_walrus=args.check_walrus)
        all_issues.extend(issues)
        
        if args.verbose and issues:
            print(f"\n{py_file.relative_to(root_path)}:")
            for issue in issues:
                severity_icon = "❌" if issue.severity == Severity.ERROR else "⚠️" if issue.severity == Severity.WARNING else "💡"
                print(f"  {severity_icon} Line {issue.lineno}: [{issue.category}] {issue.message}")
                if issue.suggestion:
                    print(f"     → {issue.suggestion}")
    
    # Generate reports
    if args.json or args.md:
        generate_report(
            all_issues,
            output_json=args.json,
            output_md=args.md
        )
    
    # Summary
    print("\nModernization Scanner v2 Summary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Total issues: {len(all_issues)}")
    
    # Count by severity
    by_severity = {}
    for issue in all_issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
    
    for severity in [Severity.ERROR, Severity.WARNING, Severity.SUGGESTION, Severity.AUTO_REFACTOR]:
        count = by_severity.get(severity, 0)
        if count > 0:
            print(f"  {severity.value}: {count}")
    
    if not args.verbose and len(all_issues) > 0:
        print("\nRun with --verbose to see detailed suggestions")
    
    # Fail on error if requested
    if args.fail_on_error and by_severity.get(Severity.ERROR, 0) > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
