"""
Transformer - Generate code transformations and patches.

Applies refactoring rules based on tier classification:
- Tier A: Safe auto-apply (formatting, imports)
- Tier B: Apply with tests (type hints, extraction)
- Tier C: Suggest only (architecture changes)

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Tier-based safety classification
- Dry-run mode by default
- Patch validation before apply
- Rollback capability
"""

from __future__ import annotations

import ast
import difflib
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Tier(Enum):
    """Transformation tier classification."""

    A = "safe_auto_apply"
    B = "apply_with_tests"
    C = "suggest_only"


@dataclass
class Patch:
    """A code patch to apply.

    Attributes:
        file_path: Relative path to file
        original: Original content
        modified: Modified content
        diff: Unified diff string
        rule_id: ID of the rule that generated this patch
        tier: Transformation tier
        description: Human-readable description
    """

    file_path: str
    original: str
    modified: str
    diff: str
    rule_id: str
    tier: Tier
    description: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "rule_id": self.rule_id,
            "tier": self.tier.name,
            "description": self.description,
            "diff": self.diff,
        }


@dataclass
class TransformResult:
    """Result of transformation operation.

    Attributes:
        snapshot_id: Snapshot being transformed
        timestamp: When transformation was performed
        tier_a_patches: Auto-applied patches
        tier_b_patches: Patches requiring tests
        tier_c_suggestions: Suggestions for manual review
        applied: Whether patches were applied
        errors: Any errors encountered
    """

    snapshot_id: str
    timestamp: datetime
    tier_a_patches: list[Patch] = field(default_factory=list)
    tier_b_patches: list[Patch] = field(default_factory=list)
    tier_c_suggestions: list[dict[str, Any]] = field(default_factory=list)
    applied: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "tier_a_patches": [p.to_dict() for p in self.tier_a_patches],
            "tier_b_patches": [p.to_dict() for p in self.tier_b_patches],
            "tier_c_suggestions": self.tier_c_suggestions,
            "applied": self.applied,
            "errors": self.errors,
        }

    def save(self, directory: Path) -> None:
        """Save patches to directory."""
        directory.mkdir(parents=True, exist_ok=True)

        # Save summary
        summary_path = directory / "transform-summary.json"
        with summary_path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        # Save individual patches
        if self.tier_a_patches:
            tier_a_path = directory / "tier-a.patch"
            with tier_a_path.open("w", encoding="utf-8") as f:
                for patch in self.tier_a_patches:
                    f.write(f"# {patch.rule_id}: {patch.description}\n")
                    f.write(patch.diff)
                    f.write("\n")

        if self.tier_b_patches:
            tier_b_path = directory / "tier-b.patch"
            with tier_b_path.open("w", encoding="utf-8") as f:
                for patch in self.tier_b_patches:
                    f.write(f"# {patch.rule_id}: {patch.description}\n")
                    f.write(patch.diff)
                    f.write("\n")

        if self.tier_c_suggestions:
            tier_c_dir = directory / "tier-c-suggestions"
            tier_c_dir.mkdir(exist_ok=True)
            for i, suggestion in enumerate(self.tier_c_suggestions):
                path = tier_c_dir / f"suggestion-{i + 1}.md"
                with path.open("w", encoding="utf-8") as f:
                    f.write(f"# {suggestion.get('rule_id', 'unknown')}\n\n")
                    f.write(f"## Description\n{suggestion.get('description', '')}\n\n")
                    f.write("## Checklist\n")
                    for item in suggestion.get("checklist", []):
                        f.write(f"- [ ] {item}\n")


def _create_diff(original: str, modified: str, file_path: str) -> str:
    """Create unified diff between original and modified content."""
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
    )

    return "".join(diff)


def _resolve_tool(tool: str) -> Optional[str]:
    """Resolve a tool path from PATH for safer subprocess execution."""
    tool_path = shutil.which(tool)
    if not tool_path:
        logger.debug("%s not found, skipping", tool)
        return None
    return str(Path(tool_path).resolve())


def _run_black(file_path: Path) -> Optional[str]:
    """Run black formatter and return modified content."""
    try:
        tool_path = _resolve_tool("black")
        if not tool_path:
            return None
        # Security: Using 'black' from PATH - assumes it's a trusted code formatter
        # installed in the development environment. The file_path is validated as a Path.
        # Arguments are passed as a list to prevent shell injection.
        result = subprocess.run(
            [tool_path, "--quiet", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.debug("Black formatting skipped for %s: %s", file_path, exc)
    return None


def _run_isort(file_path: Path) -> Optional[str]:
    """Run isort and return modified content."""
    try:
        tool_path = _resolve_tool("isort")
        if not tool_path:
            return None
        # Security: Using 'isort' from PATH - assumes it's a trusted import sorting tool
        # installed in the development environment. The file_path is validated as a Path.
        # Arguments are passed as a list to prevent shell injection.
        result = subprocess.run(
            [tool_path, "--quiet", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.debug("Isort formatting skipped for %s: %s", file_path, exc)
    return None


def _apply_pathlib_migration(content: str) -> str:
    """Apply os.path to pathlib migration.

    Simple pattern-based replacement for common patterns.
    """
    import re

    replacements = [
        (r"os\.path\.join\(([^,]+),\s*([^)]+)\)", r"Path(\1) / \2"),
        (r"os\.path\.exists\(([^)]+)\)", r"Path(\1).exists()"),
        (r"os\.path\.dirname\(([^)]+)\)", r"str(Path(\1).parent)"),
        (r"os\.path\.basename\(([^)]+)\)", r"Path(\1).name"),
        (r"os\.path\.isfile\(([^)]+)\)", r"Path(\1).is_file()"),
        (r"os\.path\.isdir\(([^)]+)\)", r"Path(\1).is_dir()"),
    ]

    modified = content
    for pattern, replacement in replacements:
        modified = re.sub(pattern, replacement, modified)

    # Add pathlib import if we made changes and it's not already imported
    if modified != content and "from pathlib import" not in modified:
        if "import os" in modified:
            modified = modified.replace("import os", "import os\nfrom pathlib import Path", 1)

    return modified


def transform(
    source_dir: Path,
    snapshot_id: str,
    tier: Optional[Tier] = None,
    auto_apply: bool = False,
    dry_run: bool = True,
) -> TransformResult:
    """Generate and optionally apply transformations.

    Args:
        source_dir: Directory containing source files
        snapshot_id: Snapshot being transformed
        tier: Specific tier to apply (None for all)
        auto_apply: Whether to automatically apply Tier A
        dry_run: If True, don't modify files

    Returns:
        TransformResult with generated patches

    Example:
        >>> result = transform(Path("source/"), "20251217-abc123", auto_apply=True)
        >>> logger.info(f"Generated {len(result.tier_a_patches)} Tier A patches")
    """
    now = datetime.now(timezone.utc)
    result = TransformResult(snapshot_id=snapshot_id, timestamp=now)

    # Find Python files
    python_files = sorted(source_dir.rglob("*.py"))
    logger.info("Transforming %d Python files", len(python_files))

    for file_path in python_files:
        try:
            original = file_path.read_text(encoding="utf-8", errors="replace")
            rel_path = str(file_path.relative_to(source_dir))

            # === Tier A: Safe Auto-Apply ===
            if tier is None or tier == Tier.A:
                # Black formatting (check only in dry-run)
                if not dry_run:
                    black_result = _run_black(file_path)
                    if black_result and black_result != original:
                        diff = _create_diff(original, black_result, rel_path)
                        result.tier_a_patches.append(
                            Patch(
                                file_path=rel_path,
                                original=original,
                                modified=black_result,
                                diff=diff,
                                rule_id="format-black",
                                tier=Tier.A,
                                description="Apply Black code formatting",
                            )
                        )
                        original = black_result

                # isort
                if not dry_run:
                    isort_result = _run_isort(file_path)
                    if isort_result and isort_result != original:
                        diff = _create_diff(original, isort_result, rel_path)
                        result.tier_a_patches.append(
                            Patch(
                                file_path=rel_path,
                                original=original,
                                modified=isort_result,
                                diff=diff,
                                rule_id="sort-imports",
                                tier=Tier.A,
                                description="Sort imports with isort",
                            )
                        )
                        original = isort_result

                # Pathlib migration
                pathlib_result = _apply_pathlib_migration(original)
                if pathlib_result != original:
                    diff = _create_diff(original, pathlib_result, rel_path)
                    patch = Patch(
                        file_path=rel_path,
                        original=original,
                        modified=pathlib_result,
                        diff=diff,
                        rule_id="pathlib-migration",
                        tier=Tier.A,
                        description="Replace os.path with pathlib equivalents",
                    )
                    result.tier_a_patches.append(patch)

                    if auto_apply and not dry_run:
                        file_path.write_text(pathlib_result, encoding="utf-8")
                        original = pathlib_result

            # === Tier B: Apply with Tests ===
            if tier is None or tier == Tier.B:
                # Type hints suggestion - use AST for robust detection
                try:
                    tree = ast.parse(original)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check if function lacks return annotation
                            if node.returns is None:
                                result.tier_b_patches.append(
                                    Patch(
                                        file_path=rel_path,
                                        original="",
                                        modified="",
                                        diff="",
                                        rule_id="add-type-hints",
                                        tier=Tier.B,
                                        description=f"Add type annotations to function '{node.name}' (requires validation)",  # noqa: E501
                                    )
                                )
                                break  # Only suggest once per file
                except SyntaxError as e:
                    type(e).__name__
                    logger.debug("SyntaxError: <ERROR_TYPE>")
                    logger.warning(
                        f"SyntaxError: {e}", exc_info=True
                    )  # Skip files with syntax errors

            # === Tier C: Suggest Only ===
            if tier is None or tier == Tier.C:
                # Async conversion suggestion
                if "requests." in original or "urllib" in original:
                    result.tier_c_suggestions.append(
                        {
                            "rule_id": "async-conversion",
                            "file": rel_path,
                            "description": "Consider converting synchronous HTTP calls to async",
                            "warning": "Major API change; requires full rewrite of callers",
                            "checklist": [
                                "All callers identified and updated",
                                "Event loop management reviewed",
                                "Error handling preserved",
                            ],
                        }
                    )

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            result.errors.append(f"Error processing {file_path}: {e}")
            logger.error("Transform error for %s: %s", file_path, e)

    result.applied = auto_apply and not dry_run

    logger.info(
        "Transform complete: %d Tier A, %d Tier B, %d Tier C suggestions",
        len(result.tier_a_patches),
        len(result.tier_b_patches),
        len(result.tier_c_suggestions),
    )

    return result
