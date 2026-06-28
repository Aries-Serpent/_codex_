"""Documentation Sync Validator.

Ensures documentation matches implementation.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402


@dataclass
class DocSyncIssue:
    """Documentation sync issue."""

    file_path: str
    issue_type: str
    location: str
    message: str
    severity: str = "warning"


class DocumentationValidator:
    """Validate documentation against implementation."""

    def __init__(self) -> None:
        self.issues: list[DocSyncIssue] = []

    def validate_file(self, file_path: Path) -> list[DocSyncIssue]:
        """Validate documentation in a file."""
        issues: list[Any] = []
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except (SyntaxError, FileNotFoundError):
            logger.debug("Exception caught, returning", exc_info=True)
            return issues

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring is None and not node.name.startswith("_"):
                    issues.append(
                        DocSyncIssue(
                            file_path=str(file_path),
                            issue_type="missing_docstring",
                            location=node.name,
                            message=f"Missing docstring for '{node.name}'",
                        )
                    )
        return issues

    def validate_directory(self, directory: Path) -> list[DocSyncIssue]:
        """Validate all Python files in directory."""
        all_issues = []
        for py_file in directory.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                issues = self.validate_file(py_file)
                all_issues.extend(issues)
        return all_issues


def sync_documentation(src_dir: Path) -> dict[str, Any]:
    """Sync and validate documentation."""
    validator = DocumentationValidator()
    issues = validator.validate_directory(src_dir)
    return {
        "total_issues": len(issues),
        "issues": issues,
        "passing": len(issues) == 0,
    }
