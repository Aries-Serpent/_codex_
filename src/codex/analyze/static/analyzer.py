"""Compatibility wrapper for the canonical static analyzer implementation."""

import ast
import json
import logging
import shutil
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from aries_serpent_core.analyze.static.analyzer import (
    DEFAULT_TRUSTED_DIRS,
    MAX_FILE_SIZE_KB,
    MAX_FILES_TO_ANALYZE,
    TRUSTED_TOOL_DIRS,
    ComplexityMetrics,
    FileAnalysis,
    LintIssue,
    SecurityIssue,
    StaticReport,
    _calculate_complexity,
    _count_lines,
    _extract_exports,
    _extract_imports,
)

logger = logging.getLogger(__name__)


def _resolve_tool(tool: str, trusted_dirs: Optional[list[Any]] = None) -> Optional[str]:
    """Resolve a tool path while respecting the repo's trusted-directory policy."""
    tool_path = shutil.which(tool)
    if not tool_path:
        logger.warning("%s not found, skipping", tool)
        return None

    resolved_path = Path(tool_path).resolve()
    if trusted_dirs:
        is_trusted = any(
            resolved_path.is_relative_to(Path(trusted_dir).resolve())
            for trusted_dir in trusted_dirs
        )
        if not is_trusted:
            logger.warning(
                "%s resolved to %s which is not in any configured trusted directory, skipping",
                tool,
                resolved_path,
            )
            return None

    return str(resolved_path)


def _run_ruff(source_dir: Path) -> list[LintIssue]:
    """Run ruff and collect lint findings."""
    issues: list[Any] = []

    try:
        if not source_dir.exists():
            logger.warning("Source directory %s does not exist; skipping ruff", source_dir)
            return issues
        tool_path = _resolve_tool("ruff", trusted_dirs=TRUSTED_TOOL_DIRS)
        if not tool_path:
            return issues
        result = subprocess.run(
            [tool_path, "check", "--output-format=json", str(source_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.stdout:
            data = json.loads(result.stdout)
            for item in data:
                issues.append(
                    LintIssue(
                        rule=item.get("code", ""),
                        severity="warning" if item.get("code", "").startswith("W") else "error",
                        line=item.get("location", {}).get("row", 0),
                        column=item.get("location", {}).get("column", 0),
                        message=item.get("message", ""),
                        file_path=item.get("filename", ""),
                    )
                )
    except FileNotFoundError:
        logger.warning("ruff not found, skipping lint check")
    except subprocess.TimeoutExpired:
        logger.warning("ruff timed out")
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.warning("ruff failed: %s", exc)

    return issues


def _run_bandit(source_dir: Path) -> list[SecurityIssue]:
    """Run bandit and collect security findings."""
    issues: list[Any] = []

    try:
        if not source_dir.exists():
            logger.warning("Source directory %s does not exist; skipping bandit", source_dir)
            return issues
        tool_path = _resolve_tool("bandit", trusted_dirs=TRUSTED_TOOL_DIRS)
        if not tool_path:
            return issues
        result = subprocess.run(
            [tool_path, "-r", "-f", "json", str(source_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.stdout:
            data = json.loads(result.stdout)
            for item in data.get("results", []):
                issues.append(
                    SecurityIssue(
                        tool="bandit",
                        rule_id=item.get("test_id", ""),
                        severity=item.get("issue_severity", "medium").lower(),
                        line=item.get("line_number", 0),
                        message=item.get("issue_text", ""),
                        file_path=item.get("filename", ""),
                    )
                )
    except FileNotFoundError:
        logger.warning("bandit not found, skipping security scan")
    except subprocess.TimeoutExpired:
        logger.warning("bandit timed out")
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.warning("bandit failed: %s", exc)

    return issues


def analyze_file(file_path: Path, base_dir: Path) -> Optional[FileAnalysis]:
    """Analyze a single Python file, normalizing indentation before AST parsing."""
    try:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            logger.warning("Skipping large file: %s (%.1f KB)", file_path, size_kb)
            return None

        content = textwrap.dedent(file_path.read_text(encoding="utf-8", errors="replace"))
        loc, sloc = _count_lines(content)

        try:
            tree = ast.parse(content)
        except SyntaxError as exc:
            logger.warning("Syntax error in %s: %s", file_path, exc)
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
            lint_issues=[],
            security_issues=[],
        )
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.error("Error analyzing %s: %s", file_path, exc)
        return None


def analyze(
    source_dir: Path,
    snapshot_id: str,
    run_lint: bool = True,
    run_security: bool = True,
) -> StaticReport:
    """Run static analysis on a source directory."""
    now = datetime.now(timezone.utc)
    files: list[FileAnalysis] = []

    python_files = sorted(source_dir.rglob("*.py"))[:MAX_FILES_TO_ANALYZE]
    logger.info("Analyzing %d Python files in %s", len(python_files), source_dir)

    for file_path in python_files:
        analysis = analyze_file(file_path, source_dir)
        if analysis:
            files.append(analysis)

    lint_issues: list[LintIssue] = []
    if run_lint:
        lint_issues = _run_ruff(source_dir)
        for issue in lint_issues:
            for file_analysis in files:
                if issue.file_path.endswith(file_analysis.path):
                    file_analysis.lint_issues.append(issue)

    security_issues: list[SecurityIssue] = []
    if run_security:
        security_issues = _run_bandit(source_dir)
        for issue in security_issues:  # type: ignore[assignment]
            for file_analysis in files:
                if issue.file_path.endswith(file_analysis.path):
                    file_analysis.security_issues.append(issue)  # type: ignore[arg-type]

    total_loc = sum(file_analysis.loc for file_analysis in files)
    total_sloc = sum(file_analysis.sloc for file_analysis in files)
    avg_complexity = (
        sum(file_analysis.complexity.cyclomatic for file_analysis in files) / len(files)
        if files
        else 0
    )

    summary = {
        "total_files": len(files),
        "total_loc": total_loc,
        "total_sloc": total_sloc,
        "avg_complexity": round(avg_complexity, 2),
        "lint_error_count": len([issue for issue in lint_issues if issue.severity == "error"]),
        "lint_warning_count": len([issue for issue in lint_issues if issue.severity == "warning"]),
        "security_issue_count": len(security_issues),
        "security_critical_count": len([issue for issue in security_issues if issue.severity == "critical"]),
        "security_high_count": len([issue for issue in security_issues if issue.severity == "high"]),
    }

    return StaticReport(
        snapshot_id=snapshot_id,
        timestamp=now,
        files=files,
        summary=summary,
    )


__all__ = [
    "DEFAULT_TRUSTED_DIRS",
    "MAX_FILE_SIZE_KB",
    "MAX_FILES_TO_ANALYZE",
    "TRUSTED_TOOL_DIRS",
    "ComplexityMetrics",
    "FileAnalysis",
    "LintIssue",
    "SecurityIssue",
    "StaticReport",
    "_calculate_complexity",
    "_count_lines",
    "_extract_exports",
    "_extract_imports",
    "_resolve_tool",
    "_run_bandit",
    "_run_ruff",
    "analyze",
    "analyze_file",
    "logger",
]
