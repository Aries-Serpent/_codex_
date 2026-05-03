#!/usr/bin/env python3
"""
Redundant Code

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/linters/redundant_code.py [options]

    Examples:
    $ python scripts/linters/redundant_code.py --help

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



import argparse
import ast
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class RedundantCodeDetector(ast.NodeVisitor):
    """AST visitor to detect redundant code patterns."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[tuple[int, str, str]] = []  # (line, type, message)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect redundant pass in exception handlers."""
        for handler in node.handlers:
            if len(handler.body) == 2:
                # Check if first statement is a logging/print call
                first_stmt = handler.body[0]
                second_stmt = handler.body[1]

                is_logging = False
                if isinstance(first_stmt, ast.Expr):
                    if isinstance(first_stmt.value, ast.Call):
                        call = first_stmt.value
                        if isinstance(call.func, ast.Attribute):
                            if call.func.attr in ["debug", "info", "warning", "error", "critical"]:
                                is_logging = True
                        elif isinstance(call.func, ast.Name):
                            if call.func.id == "print":
                                is_logging = True

                # Check if second statement is redundant pass
                if is_logging and isinstance(second_stmt, ast.Pass):
                    self.issues.append(
                        (
                            second_stmt.lineno,
                            "redundant_pass",
                            "Redundant pass statement after logging/print in exception handler",
                        )
                    )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detect redundant return None at end of function."""
        if node.body:
            last_stmt = node.body[-1]

            # Check for explicit return None at end
            if isinstance(last_stmt, ast.Return) and (last_stmt.value is None or (
                isinstance(last_stmt.value, ast.Constant) and last_stmt.value.value is None
            )):
                # Check if function has other return statements
                has_other_returns = any(
                    isinstance(stmt, ast.Return) and stmt != last_stmt
                    for stmt in ast.walk(node)
                )

                if not has_other_returns:
                    self.issues.append(
                        (
                            last_stmt.lineno,
                            "redundant_return_none",
                            "Redundant 'return None' at end of function (implicit return)",
                        )
                    )

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Detect unnecessary else after return/raise."""
        # Check if all paths in if-block end with return/raise
        if node.orelse and self._all_paths_exit(node.body):
            first_else_line = node.orelse[0].lineno if node.orelse else None
            if first_else_line:
                self.issues.append(
                    (
                        first_else_line,
                        "unnecessary_else",
                        "Unnecessary else block after return/raise (consider unindenting)",
                    )
                )

        self.generic_visit(node)

    def _all_paths_exit(self, stmts: list[ast.stmt]) -> bool:
        """Check if all paths in statement list end with return/raise."""
        if not stmts:
            return False

        last_stmt = stmts[-1]

        if isinstance(last_stmt, (ast.Return, ast.Raise)):
            return True

        if isinstance(last_stmt, ast.If):
            # Both if and else must exit
            if_exits = self._all_paths_exit(last_stmt.body)
            else_exits = self._all_paths_exit(last_stmt.orelse) if last_stmt.orelse else False
            return if_exits and else_exits

        return False


def analyze_file(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Analyze a Python file for redundant code.

    Returns:
        list of (line_number, issue_type, message) tuples
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return []

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        detector = RedundantCodeDetector(str(file_path))
        detector.visit(tree)

        return detector.issues

    except (SyntaxError, UnicodeDecodeError) as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Could not parse {file_path}: {e}")
        return []


def fix_redundant_pass(
    file_path: Path, issues: list[tuple[int, str, str]], dry_run: bool = True
) -> bool:
    """
    Fix redundant pass statements.

    Returns:
        True if fixes were applied, False otherwise
    """
    if not issues:
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Filter for redundant_pass issues
        pass_issues = [issue for issue in issues if issue[1] == "redundant_pass"]
        if not pass_issues:
            return False

        # Remove lines in reverse order to maintain line numbers
        for line_num, _, _ in sorted(pass_issues, reverse=True):
            if 1 <= line_num <= len(lines) and lines[line_num - 1].strip() == "pass":
                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would remove line {line_num}: {lines[line_num - 1].rstrip()}"
                    )
                else:
                    del lines[line_num - 1]

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            logger.info(f"Fixed {len(pass_issues)} redundant pass statement(s) in {file_path}")

        return True

    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Failed to fix {file_path}: {e}")
        return False


def process_directory(directory: Path, fix: bool = False, dry_run: bool = True) -> dict:
    """Process all Python files in a directory."""
    stats = {"total": 0, "with_issues": 0, "fixed": 0, "issues_found": 0}

    for py_file in directory.rglob("*.py"):
        stats["total"] += 1
        issues = analyze_file(py_file)

        if issues:
            stats["with_issues"] += 1
            stats["issues_found"] += len(issues)

            logger.info(f"\n{py_file}:")
            for line, issue_type, message in issues:
                logger.info(f"  Line {line} [{issue_type}]: {message}")

            if fix and fix_redundant_pass(py_file, issues, dry_run):
                stats["fixed"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Detect and fix redundant code patterns")
    parser.add_argument("--file", type=Path, help="Python file to analyze")
    parser.add_argument("--directory", type=Path, help="Directory to scan recursively")
    # Use mutually exclusive group for clarity
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes to redundant pass statements (modifies files)",
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files (explicit dry-run mode)",
    )

    args = parser.parse_args()

    # Default to dry-run if neither --fix nor --dry-run is specified
    dry_run = not args.fix

    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("Use --fix to apply changes")
        logger.info("=" * 60)
        logger.info("")

    if args.file:
        issues = analyze_file(args.file)

        if issues:
            logger.info(f"\nFile: {args.file}")
            for line, issue_type, message in issues:
                logger.info(f"  Line {line} [{issue_type}]: {message}")

            if args.fix:
                fix_redundant_pass(args.file, issues, dry_run)
        else:
            logger.info(f"✅ {args.file}: No redundant code detected")

        return 0

    if args.directory:
        stats = process_directory(args.directory, args.fix, dry_run)

        logger.info(f"\n{'='*60}")
        logger.info("Summary:")
        logger.info(f"  Total files: {stats['total']}")
        logger.info(f"  Files with issues: {stats['with_issues']}")
        logger.info(f"  Total issues: {stats['issues_found']}")
        if args.fix:
            logger.info(f"  Files fixed: {stats['fixed']}")
        logger.info(f"{'='*60}")

        return 0 if stats["issues_found"] == 0 else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
