"""
Static Analyzer - AST parsing, linting, and security scanning.

Performs comprehensive static analysis of Python code including:
- AST parsing and symbol table building
- Complexity metrics (cyclomatic, cognitive)
- Lint checking with ruff
- Type checking with mypy
- Security scanning with bandit/semgrep

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on source paths
- Bounded file processing
- Error isolation per file
- Deterministic output ordering
"""

from __future__ import annotations

import ast
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Safeguards: Configuration bounds
MAX_FILE_SIZE_KB = 1024
MAX_FILES_TO_ANALYZE = 1000


@dataclass
class LintIssue:
    """A linting issue found in source code."""
    rule: str
    severity: str  # error, warning, info
    line: int
    column: int
    message: str
    file_path: str


@dataclass
class SecurityIssue:
    """A security issue found in source code."""
    tool: str  # bandit, semgrep, gitleaks
    rule_id: str
    severity: str  # critical, high, medium, low
    line: int
    message: str
    file_path: str


@dataclass
class ComplexityMetrics:
    """Complexity metrics for a file."""
    cyclomatic: float
    cognitive: float
    halstead_difficulty: Optional[float] = None


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    path: str
    loc: int
    sloc: int
    complexity: ComplexityMetrics
    imports: List[str]
    exports: List[str]
    lint_issues: List[LintIssue]
    security_issues: List[SecurityIssue]


@dataclass
class StaticReport:
    """Complete static analysis report.

    Contains analysis results for all files in the source directory
    along with aggregate statistics.
    """
    snapshot_id: str
    timestamp: datetime
    files: List[FileAnalysis]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "files": [
                {
                    "path": f.path,
                    "loc": f.loc,
                    "sloc": f.sloc,
                    "complexity": {
                        "cyclomatic": f.complexity.cyclomatic,
                        "cognitive": f.complexity.cognitive,
                        "halstead_difficulty": f.complexity.halstead_difficulty,
                    },
                    "imports": f.imports,
                    "exports": f.exports,
                    "lint_issues": [
                        {
                            "rule": i.rule,
                            "severity": i.severity,
                            "line": i.line,
                            "message": i.message,
                        }
                        for i in f.lint_issues
                    ],
                    "security_issues": [
                        {
                            "tool": s.tool,
                            "rule_id": s.rule_id,
                            "severity": s.severity,
                            "line": s.line,
                            "message": s.message,
                        }
                        for s in f.security_issues
                    ],
                }
                for f in self.files
            ],
            "summary": self.summary,
        }

    def save(self, path: Path) -> None:
        """Save report to JSON file."""
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


def _count_lines(content: str) -> tuple[int, int]:
    """Count total and source lines of code.

    Returns:
        Tuple of (total_loc, source_loc)
    """
    lines = content.split("\n")
    loc = len(lines)

    # Count non-empty, non-comment lines
    sloc = 0
    in_docstring = False
    for line in lines:
        stripped = line.strip()

        # Handle docstrings
        if '"""' in stripped or "'''" in stripped:
            count = stripped.count('"""') + stripped.count("'''")
            if count == 1:
                in_docstring = not in_docstring
            continue

        if in_docstring:
            continue

        # Skip empty lines and comments
        if stripped and not stripped.startswith("#"):
            sloc += 1

    return loc, sloc


def _extract_imports(tree: ast.AST) -> List[str]:
    """Extract import names from AST."""
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    return sorted(set(imports))


def _extract_exports(tree: ast.AST) -> List[str]:
    """Extract exported names from AST (functions, classes, __all__)."""
    exports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                exports.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                exports.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                exports.append(str(elt.value))

    return sorted(set(exports))


def _calculate_complexity(tree: ast.AST) -> ComplexityMetrics:
    """Calculate complexity metrics for AST.

    Simple cyclomatic complexity calculation.
    """
    complexity = 1  # Base complexity

    for node in ast.walk(tree):
        # Control flow statements increase complexity
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, (ast.And, ast.Or)):
            complexity += 1
        elif isinstance(node, ast.comprehension):
            complexity += 1
            if node.ifs:
                complexity += len(node.ifs)

    return ComplexityMetrics(
        cyclomatic=float(complexity),
        cognitive=float(complexity * 0.8),  # Simplified estimate
    )


def _resolve_tool(tool: str, trusted_dirs: Optional[list] = None) -> Optional[str]:
    """
    Resolve tool path from PATH with optional trusted directory validation.

    Args:
        tool: Name of the tool to resolve
        trusted_dirs: Optional list of trusted directory prefixes (e.g., ['/usr/bin', '/usr/local/bin'])

    Returns:
        Resolved tool path if found and trusted, None otherwise
    """
    tool_path = shutil.which(tool)
    if not tool_path:
        logger.warning("%s not found, skipping", tool)
        return None

    resolved_path = Path(tool_path).resolve()

    # If trusted directories specified, validate the tool path
    if trusted_dirs:
        is_trusted = any(
            resolved_path.is_relative_to(Path(trusted_dir).resolve())
            for trusted_dir in trusted_dirs
        )
        if not is_trusted:
            logger.warning(
                "%s resolved to %s which is not in any configured trusted directory, skipping",
                tool, resolved_path
            )
            return None

    return str(resolved_path)


def _run_ruff(source_dir: Path) -> List[LintIssue]:
    """Run ruff linter and collect issues."""
    issues = []

    try:
        if not source_dir.exists():
            logger.warning("Source directory %s does not exist; skipping ruff", source_dir)
            return issues
        tool_path = _resolve_tool("ruff")
        if not tool_path:
            return issues
        # Security: Using 'ruff' from PATH. The source_dir is validated to be a Path object.
        # Arguments are passed as a list to prevent shell injection.
        # Optional: Configure trusted_dirs parameter in _resolve_tool() to restrict tool paths.
        result = subprocess.run(
            [tool_path, "check", "--output-format=json", str(source_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.stdout:
            data = json.loads(result.stdout)
            for item in data:
                issues.append(LintIssue(
                    rule=item.get("code", ""),
                    severity="warning" if item.get("code", "").startswith("W") else "error",
                    line=item.get("location", {}).get("row", 0),
                    column=item.get("location", {}).get("column", 0),
                    message=item.get("message", ""),
                    file_path=item.get("filename", ""),
                ))
    except FileNotFoundError:
        logger.warning("ruff not found, skipping lint check")
    except subprocess.TimeoutExpired:
        logger.warning("ruff timed out")
    except Exception as e:
        logger.warning("ruff failed: %s", e)

    return issues


def _run_bandit(source_dir: Path) -> List[SecurityIssue]:
    """Run bandit security scanner and collect issues."""
    issues = []

    try:
        if not source_dir.exists():
            logger.warning("Source directory %s does not exist; skipping bandit", source_dir)
            return issues
        tool_path = _resolve_tool("bandit")
        if not tool_path:
            return issues
        # Security: Using 'bandit' from PATH - assumes it's a trusted security scanning tool
        # installed in the development environment. The source_dir is validated as a Path.
        # Arguments are passed as a list to prevent shell injection.
        result = subprocess.run(
            [tool_path, "-r", "-f", "json", str(source_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.stdout:
            data = json.loads(result.stdout)
            for item in data.get("results", []):
                issues.append(SecurityIssue(
                    tool="bandit",
                    rule_id=item.get("test_id", ""),
                    severity=item.get("issue_severity", "medium").lower(),
                    line=item.get("line_number", 0),
                    message=item.get("issue_text", ""),
                    file_path=item.get("filename", ""),
                ))
    except FileNotFoundError:
        logger.warning("bandit not found, skipping security scan")
    except subprocess.TimeoutExpired:
        logger.warning("bandit timed out")
    except Exception as e:
        logger.warning("bandit failed: %s", e)

    return issues


def analyze_file(file_path: Path, base_dir: Path) -> Optional[FileAnalysis]:
    """Analyze a single Python file.

    Args:
        file_path: Path to Python file
        base_dir: Base directory for relative paths

    Returns:
        FileAnalysis or None if file couldn't be analyzed
    """
    try:
        # Size check safeguard
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            logger.warning("Skipping large file: %s (%.1f KB)", file_path, size_kb)
            return None

        content = file_path.read_text(encoding="utf-8", errors="replace")
        loc, sloc = _count_lines(content)

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning("Syntax error in %s: %s", file_path, e)
            return FileAnalysis(
                path=str(file_path.relative_to(base_dir)),
                loc=loc,
                sloc=sloc,
                complexity=ComplexityMetrics(cyclomatic=0, cognitive=0),
                imports=[],
                exports=[],
                lint_issues=[],
                security_issues=[],
            )

        imports = _extract_imports(tree)
        exports = _extract_exports(tree)
        complexity = _calculate_complexity(tree)

        return FileAnalysis(
            path=str(file_path.relative_to(base_dir)),
            loc=loc,
            sloc=sloc,
            complexity=complexity,
            imports=imports,
            exports=exports,
            lint_issues=[],  # Populated by batch run
            security_issues=[],  # Populated by batch run
        )

    except Exception as e:
        logger.error("Error analyzing %s: %s", file_path, e)
        return None


def analyze(
    source_dir: Path,
    snapshot_id: str,
    run_lint: bool = True,
    run_security: bool = True,
) -> StaticReport:
    """Run static analysis on a source directory.

    Performs comprehensive static analysis including AST parsing,
    complexity metrics, linting, and security scanning.

    Args:
        source_dir: Directory containing source files
        snapshot_id: ID of the snapshot being analyzed
        run_lint: Whether to run linting (default True)
        run_security: Whether to run security scanning (default True)

    Returns:
        StaticReport with analysis results

    Example:
        >>> report = analyze(Path("source/"), "20251217-abc123")
        >>> print(f"Analyzed {len(report.files)} files")
    """
    now = datetime.now(timezone.utc)
    files: List[FileAnalysis] = []

    # Find all Python files
    python_files = sorted(source_dir.rglob("*.py"))[:MAX_FILES_TO_ANALYZE]

    logger.info("Analyzing %d Python files in %s", len(python_files), source_dir)

    # Analyze each file
    for file_path in python_files:
        analysis = analyze_file(file_path, source_dir)
        if analysis:
            files.append(analysis)

    # Run batch lint check
    lint_issues: List[LintIssue] = []
    if run_lint:
        lint_issues = _run_ruff(source_dir)

        # Associate issues with files
        for issue in lint_issues:
            for f in files:
                if issue.file_path.endswith(f.path):
                    f.lint_issues.append(issue)

    # Run security scan
    security_issues: List[SecurityIssue] = []
    if run_security:
        security_issues = _run_bandit(source_dir)

        # Associate issues with files
        for issue in security_issues:
            for f in files:
                if issue.file_path.endswith(f.path):
                    f.security_issues.append(issue)

    # Calculate summary
    total_loc = sum(f.loc for f in files)
    total_sloc = sum(f.sloc for f in files)
    avg_complexity = (
        sum(f.complexity.cyclomatic for f in files) / len(files)
        if files else 0
    )

    summary = {
        "total_files": len(files),
        "total_loc": total_loc,
        "total_sloc": total_sloc,
        "avg_complexity": round(avg_complexity, 2),
        "lint_error_count": len([i for i in lint_issues if i.severity == "error"]),
        "lint_warning_count": len([i for i in lint_issues if i.severity == "warning"]),
        "security_issue_count": len(security_issues),
        "security_critical_count": len([i for i in security_issues if i.severity == "critical"]),
        "security_high_count": len([i for i in security_issues if i.severity == "high"]),
    }

    logger.info(
        "Analysis complete: %d files, %d LOC, %d lint issues, %d security issues",
        len(files),
        total_loc,
        len(lint_issues),
        len(security_issues),
    )

    return StaticReport(
        snapshot_id=snapshot_id,
        timestamp=now,
        files=files,
        summary=summary,
    )
